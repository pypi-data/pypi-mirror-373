from logbook import Logger

from hansken import fetch
from hansken.remote import Connection, ImportStrategy, ProjectContext
from hansken.tool import add_command, prompt_verify_key
from hansken.util import b64decode


log = Logger(__name__)


def run_import_command(args):
    """
    Starts the import of a project. Requires a keystore
    to work for encrypted images; keys will be fetched automatically.

    :param args: an `argparse.Namespace` object carrying command line arguments
    """
    # check that we'll have an endpoint and a project (error message emulated to look like argparse's own messages)
    if not args.endpoint:
        import_parser.error('the following argument is required: --endpoint ENDPOINT')
    if not args.project:
        import_parser.error('the following arguments is required: PROJECT')
    if not args.keystore:
        import_parser.error('the following argument is required: --keystore ENDPOINT')
    if not args.preference:
        import_parser.error('the following argument is required: --preference ENDPOINT')
    if not args.user_export_key:
        import_parser.error('the following argument is required: USER_EXPORT_KEY')

    user_export_key = args.user_export_key

    if callable(user_export_key):
        user_export_key = user_export_key()

    with Connection(
        args.endpoint, keystore_url=args.keystore, preference_url=args.preference, auth=args.auth, verify=args.verify
    ) as connection:
        start_import(
            connection,
            b64decode(user_export_key, validate=True),
            project=args.project,
            export_file=args.file,
            wait_for_import=args.await_import,
            apply_import=args.apply_import,
            wait_for_apply=args.await_apply,
            project_metadata_import_strategy=ImportStrategy(args.project_import_strategy),
            images_metadata_import_strategy=ImportStrategy(args.images_import_strategy),
        )


def start_import(
    connection,
    user_export_key,
    project,
    export_file,
    wait_for_import,
    apply_import,
    wait_for_apply,
    project_metadata_import_strategy,
    images_metadata_import_strategy,
):
    """
    Starts an import for the given project. The image keys for the project are
    retrieved from the keystore. An export_key has to be provided to decrypt the export.

    :param connection: an instance of `.Connection`
    :param user_export_key: crypto key in binary (`bytes`) for decrypting the export
    :param project: project to import into
    :param export_file: export file to import
    :param apply_import: boolean indicating if the import should only be prepared or also be applied
    :param wait_for_apply: boolean indicating if the tool should wait for the import apply to finish before returning
    :param: project_metadata_import_strategy: import strategy for the project data in the export
    :param: images_metadata_import_strategy: import strategy for the image data in the export
    :return: task_id of either the import prepare task or (if enabled) the import apply task
    """
    with ProjectContext(connection, project) as context:
        task_id = context.connection.prepare_project_import(project, user_export_key, export_file)

        if wait_for_import or apply_import:
            try:
                task_status = context.connection.wait_for_task(task_id)
            except Exception:
                raise ValueError(f'error waiting for import prepare task ({task_id}) to complete')

            if task_status != 'completed':
                raise ValueError(f'import prepare task ({task_id}) not completed successfully: {task_status}')

        if apply_import:
            task_id = context.connection.apply_project_import(
                project,
                user_export_key,
                task_id,
                fetch,
                project_metadata_import_strategy,
                images_metadata_import_strategy,
            )

            if wait_for_apply:
                try:
                    task_status = context.connection.wait_for_task(task_id)
                except Exception:
                    raise ValueError(f'error waiting for import apply task ({task_id}) to complete')

                if task_status != 'completed':
                    raise ValueError(f'import apply task ({task_id}) not completed successfully: {task_status}')

        return task_id


import_parser = add_command('import', run_import_command, help='start import of a project')
import_parser.add_argument('file', metavar='FILE', help='local export file to import')
import_parser.add_argument(
    '-k',
    '--user-export-key',
    dest='user_export_key',
    metavar='USER_EXPORT_KEY',
    help='user provided key to decrypt export (base64-encoded).',
)
import_parser.add_argument(
    '-K',
    '--prompt-user-export-key',
    dest='user_export_key',
    action='store_const',
    const=prompt_verify_key,
    help='prompt for a user export key (base64-encoded)',
)
import_parser.add_argument(
    '--no-wait-for-import',
    dest='await_import',
    action='store_false',
    help='do not wait till import prepare finishes (setting is ignored if apply is required)',
    default=True,
)
import_parser.add_argument(
    '--no-apply-import',
    dest='apply_import',
    action='store_false',
    help='only prepare import but do not apply to project',
    default=True,
)
import_parser.add_argument(
    '--no-wait-for-apply',
    dest='await_apply',
    action='store_false',
    help='do not wait till import apply finishes (which is itself not a guarantor of success)',
    default=True,
)
import_parser.add_argument(
    '--project-metadata-import-strategy',
    dest='project_import_strategy',
    choices=[strategy.value for strategy in list(ImportStrategy)],
    help='strategy for how to use exported project metadata during the import',
    default=ImportStrategy.UPDATE.value,
)
import_parser.add_argument(
    '--image-metadata-import-strategy',
    dest='images_import_strategy',
    choices=[strategy.value for strategy in list(ImportStrategy)],
    help='strategy for how to use exported images metadata during the import',
    default=ImportStrategy.UPDATE.value,
)
