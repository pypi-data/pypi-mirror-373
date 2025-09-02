from datetime import datetime

from ..file_helper import delete_files
from ..monica import add_to_journal
from ..todoist import add_note_with_attachement, add_to_todoist
from ..transcriber import get_recognized_text
from ..logging import setup_logging

logger = setup_logging(__file__)

def get_meditation_logs(file_path, file_name):
    print(file_path)
    date = datetime.strptime(file_name[:-4], "%Y-%m-%d-%H-%M-%S")
    recognized_text, wav = get_recognized_text(file_path)
    if recognized_text:
        add_to_journal(recognized_text, date)
        item = add_to_todoist(
            "'{recognized_text}' was recorded during meditation at '{date}'. Anything to review?".format(
                date=date.strftime("%Y-%m-%d %H:%M:%S"), recognized_text=recognized_text
            )
        )
        add_note_with_attachement(item.id, file_path)
        delete_files([file_path, wav])
        return "Recording from '{date}' with content '{text}' was added to journal and Todoist.".format(
            date=date, text=recognized_text
        )
    else:
        delete_files([file_path, wav])
        return "Recording from {date} was not recognized and therefore not added to journal or Todoist.".format(
            date=date
        )

def get_logs_from_recording(file_path, file_name, context):
    date = datetime.strptime(file_name[:-4], "%Y-%m-%d-%H-%M-%S")
    recognized_text, wav = get_recognized_text(file_path)
    if recognized_text:
        logger.info("Recognized text '{recognized_text}' for context '{context}' at '{date}'",
                    recognized_text=recognized_text,
                    context=context, date=date)
        add_to_journal(recognized_text, date, context)
        item = add_to_todoist(
            "'{recognized_text}' was recorded with the context '{context}' at '{date}'. Anything to review?".format(
                context=context,
                date=date.strftime("%Y-%m-%d %H:%M:%S"), recognized_text=recognized_text
            )
        )
        add_note_with_attachement(item.id, file_path)
        logger.info(
            "Recording from '{date}' with content '{text}' and context '{context}' was added to Micro-Journal and Todoist.".format(
                context=context, date=date, text=recognized_text))
    else:
        logger.info("No recognized text for context '{context}' at '{date}'", context=context, date=date)
    delete_files([file_path, wav])
