import os
import logging

logger = logging.getLogger(__name__)


def clean_segment(segment):
    updated_segment = segment.replace(' - ', '-').replace(' ', '_')
    replacement_segment = ''
    for c in updated_segment:
        if c is '-' or c is '_' or c is '.' or c.isalnum():
            replacement_segment += c
            continue
        replacement_segment += '_'
    return replacement_segment


def clean_path(full_path):
    dst = full_path
    final_segment = os.path.split(full_path)[-1]
    if any(not c.isalnum() for c in final_segment):
        dst = os.path.join(os.path.abspath(os.path.join(full_path, os.pardir)), clean_segment(final_segment))
    return full_path, dst


def clean(folder, is_pretend):
    logger.info('clean "%s" %s', folder, '[dry run]' if is_pretend else '')

    if not os.path.exists(folder):
        logger.error('"%s" does not exist', folder)
        return

    updates = {}
    for root, sub_dirs, files in os.walk(folder):
        src, dst = clean_path(root)
        updates[src] = dst
        for sub_dir in sub_dirs:
            src, dst = clean_path(os.path.join(root, sub_dir))
            updates[src] = dst
        for file in files:
            src, dst = clean_path(os.path.join(root, file))
            updates[src] = dst

    for src in sorted(updates.keys(), reverse=True):
        dst = updates[src]
        if src != dst:
            logger.info('%s -> %s', src, dst)
            if not is_pretend:
                os.rename(src, dst)
