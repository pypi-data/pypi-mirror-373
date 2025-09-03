import math
from os import getcwd, makedirs, path, urandom

from logbook import Logger

from hansken import fetch
from hansken.remote import Connection, ProjectContext
from hansken.tool import add_command, prompt_verify_key
from hansken.util import b64decode, b64encode


log = Logger(__name__)


def run_export_command(args):
    """
    Starts the export of a project. Requires a keystore
    to work for encrypted images; keys will be fetched automatically.

    :param args: an `argparse.Namespace` object carrying command line arguments
    """
    # check that we'll have an endpoint and a project (error message emulated to look like argparse's own messages)
    if not args.endpoint:
        export_parser.error('the following argument is required: --endpoint ENDPOINT')
    if not args.project:
        export_parser.error('the following arguments is required: PROJECT')
    if not args.keystore:
        export_parser.error('the following argument is required: --keystore ENDPOINT')
    if not args.preference:
        export_parser.error('the following argument is required: --preference ENDPOINT')
    if not args.user_export_key:
        export_parser.error('the following argument is required: USER_EXPORT_KEY')
    if args.include_image_data and args.image_id is None:
        export_parser.error('the following is argument is required when --include-image-data is true: --image-id IMAGE')

    user_export_key = args.user_export_key

    with Connection(
        args.endpoint, keystore_url=args.keystore, preference_url=args.preference, auth=args.auth, verify=args.verify
    ) as connection:
        keys_folder = None
        if callable(user_export_key):
            # generate a new key for every export if a generating lambda is provided
            user_export_key = user_export_key()
            keys_folder = args.keys_folder if args.keys_folder else args.download_folder

        export(
            connection,
            b64decode(user_export_key, validate=True),
            project=args.project,
            download_export=args.download_export,
            download_folder=args.download_folder,
            keys_folder=keys_folder,
            query=args.query,
            include_priviliged=args.include_priviliged,
            include_notes=args.include_notes,
            include_tags=args.include_tags,
            include_entities=args.include_entities,
            include_image_data=args.include_image_data,
            image_id=args.image_id,
        )


def store_user_export_key(user_export_key, keys_folder, project, task_id):
    """
    Stores the export key in the keys folder
    :param user_export_key: the key in binary (`bytes`) to write
    :param keys_folder: folder to write the user key file to
    :param project: the id of the project of the key
    :param task_id: the id of the export task
    """
    project_path = path.join(keys_folder, project)
    makedirs(project_path, exist_ok=True)
    key_file_path = path.join(project_path, f'{task_id}.export.key')
    with open(key_file_path, 'w') as f:
        f.write(b64encode(user_export_key))


def report_progress(poll_count, progress):
    if poll_count % 5 == 0:
        print(f'\r{math.floor(100 * progress)}% done...', end='', flush=True)


def export(
    connection,
    user_export_key,
    project,
    download_export,
    download_folder,
    keys_folder,
    query,
    include_priviliged,
    include_notes,
    include_tags,
    include_entities,
    include_image_data,
    image_id,
):
    """
    Starts a export for the given project. The image keys for the project are
    retrieved from the keystore. A export_key has to be provided to encrypt the export.

    :param connection: an instance of `.Connection`
    :param user_export_key: crypto key in binary (`bytes`) for encrypting the export
    :param project: project to export
    :param download_export: boolean denoting if the export should be downloaded
    :param download_folder: folder to write the export file to
    :param keys_folder: folder to write the export key to
    :param query: the query used to select all, or a subset, of traces from a project to be exported
    :param include_priviliged: if priviliged traces should be exported
    :param include_notes: if notes should be exported
    :param include_tags: if tags should be exported
    :param include_entities: if entities should be exported
    :param include_image_data: if the image data should be exported to a new sliced image.
            If true, image_id should be set, too.
    :param image_id: the UUID of the original image to generate the sliced image from.
    :return: task_id of the created export task
    """
    if download_export and not path.isdir(download_folder):
        raise ValueError(f'download folder "{download_folder}" does not exist or is not a folder')

    with ProjectContext(connection, project) as context:
        task_id = context.connection.export_project(
            project,
            user_export_key,
            fetch,
            query,
            include_priviliged,
            include_notes,
            include_tags,
            include_entities,
            include_image_data,
            image_id,
        )

        if keys_folder is not None:
            store_user_export_key(user_export_key, keys_folder, project, task_id)

        if download_export:
            log.info('polling task with id: {}', task_id)

            # wait here for the result to be available before continuing
            try:
                task_status = context.connection.wait_for_task(task_id, progress_callback=report_progress)
                print('\r100% done...')
            except Exception:
                raise ValueError(f'error waiting for export task ({task_id}) to complete')

            if task_status == 'completed':
                project_path = path.join(download_folder, project)
                makedirs(project_path, exist_ok=True)
                export_file_path = path.join(project_path, task_id + '.export')
                do_download_export(context, task_id, export_file_path)
            else:
                raise ValueError('export task not completed successfully: {task_status}')

        return task_id


def do_download_export(context, task_id, export_file_path):
    log.info('downloading export as {}', export_file_path)
    context.connection.download_export(task_id, export_file_path)
    log.info('download successful.')


export_parser = add_command('export', run_export_command, help='start export of a project')
export_parser.add_argument(
    '-k',
    '--user-export-key',
    dest='user_export_key',
    metavar='USER_EXPORT_KEY',
    default=lambda: b64encode(urandom(32)),
    help='user provided key to encrypt export (base64-encoded). By default a random key will be generated',
)
export_parser.add_argument(
    '-K',
    '--prompt-user-export-key',
    dest='user_export_key',
    action='store_const',
    const=prompt_verify_key,
    help='prompt for a user export key (base64-encoded)',
)
export_parser.add_argument(
    '-d',
    '--download-export',
    dest='download_export',
    action='store_true',
    help='enable export download.',
    default=False,
)
export_parser.add_argument(
    '-f', '--download-folder', dest='download_folder', help='folder to store the downloaded exports', default=getcwd()
)
export_parser.add_argument('--keys-folder', dest='keys_folder', help='folder to store the generated keys', default=None)
export_parser.add_argument(
    '--export-priviliged',
    dest='include_priviliged',
    action='store_true',
    help='include priviliged traces in the export',
    default=False,
)
export_parser.add_argument(
    '--export-notes',
    dest='include_notes',
    action='store_true',
    help='include notes from traces in the export',
    default=False,
)
export_parser.add_argument(
    '--export-tags',
    dest='include_tags',
    action='store_true',
    help='include tags from traces in the export',
    default=False,
)
export_parser.add_argument(
    '--no-export-entities',
    dest='include_entities',
    action='store_false',
    help='do not include entities from traces in the export',
    default=True,
)
export_parser.add_argument(
    '-q',
    '--query',
    dest='query',
    help='query used to select all, or a subset, of the traces to be exported',
    default=None,
)
export_parser.add_argument(
    '--include-image-data',
    dest='include_image_data',
    action='store_true',
    help='include the data in a newly generated sliced image; if set, also set --image-id',
    default=False,
)
export_parser.add_argument(
    '--image-id',
    dest='image_id',
    help="""the image UUID of the original image to generate a sliced image from, note that this
                           limits the results of the query to only traces from the specified image UUID; this creates a
                           portable case""",
    default=None,
)
