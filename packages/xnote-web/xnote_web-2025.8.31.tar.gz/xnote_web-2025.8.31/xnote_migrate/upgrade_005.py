# -*- coding:utf-8 -*-
# @author mark
# @since 2022/03/12 21:45:37
# @modified 2022/03/12 22:25:56
# @filename upgrade_005.py

from xutils import dbutil
from . import base
from handlers.note import dao as note_dao
from handlers.note.dao_share import share_note_to
from xutils import BaseDataRecord

def do_upgrade():
    old_key = "upgrade_005"
    new_key = "20220312_fix_note_share"
    base.move_upgrade_key(old_key, new_key)
    base.execute_upgrade(new_key, fix_note_share)

class NoteShareFromRecord(BaseDataRecord):
    def __init__(self, **kw):
        self.note_id = ""
        self.share_to_list = []
        self.update(kw)

def fix_note_share():
    dbutil.register_table("note_share_from", "分享发送者关系表 <note_share_from:from_user:note_id>")
    db = dbutil.get_table("note_share_from")
    for raw_value in db.iter(limit = -1):
        value = NoteShareFromRecord(**raw_value)
        note_id = value.note_id
        to_user_list = value.share_to_list

        note = note_dao.get_by_id(note_id)
        if note != None:
            for to_user in to_user_list:
                share_note_to(note.id, note.creator, to_user)

