from db import db


def get_all_forums():
    sql = 'SELECT id, name FROM forums ORDER BY name'
    return db.session.execute(sql).fetchall()


def get_chain_count_in_forum(forum_id):
    sql = 'SELECT COUNT(*) FROM chains WHERE forum_id = :forum_id'
    return db.session.execute(sql, {'forum_id': forum_id}).fetchone()[0]


def get_message_count_in_chain(chain_id):
    sql = 'SELECT COUNT(*) FROM messages WHERE chain_id = :chain_id'
    return db.session.execute(sql, {'chain_id': chain_id}).fetchone()[0]

# muista muokata tätä paremmaks
def get_message_count_in_forum(forum_id):
    sql = 'SELECT id FROM chains WHERE forum_id = :forum_id'
    chains = db.session.execute(sql, {'forum_id': forum_id}).fetchall()
    count = 0
    for i in chains:
        count += get_message_count_in_chain(i[0])
    return count

def get_forum_name(forum_id):
    sql = 'SELECT name FROM forums WHERE id = :forum_id'
    return db.session.execute(sql, {'forum_id': forum_id}).fetchone()

def get_chains_in_forum(forum_id):
    sql = 'SELECT id, headline FROM chains WHERE forum_id = :forum_id'
    return db.session.execute(sql, {'forum_id': forum_id}).fetchall()

def get_messages_in_chain(chain_id):
    sql = 'SELECT m.message, u.username, m.sent_at FROM messages m, users u WHERE m.chain_id = :chain_id AND u.id = m.writer_id ORDER BY m.sent_at'
    return db.session.execute(sql, {'chain_id': chain_id}).fetchall()

def get_chain_info(chain_id):
    sql = 'SELECT c.headline, u.username FROM chains c, users u WHERE c.id = :chain_id AND u.id = c.creator_id'
    return db.session.execute(sql, {'chain_id': chain_id}).fetchall()