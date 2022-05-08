from db import db
import messages as ms


def get_chains_info_in_forum(forum_id):
    sql_last_sent_message = '(SELECT TO_CHAR(m.sent_at, \'HH24:MI, Mon dd yyyy\') FROM messages m WHERE m.chain_id = c.id AND m.deleted = False ORDER BY m.sent_at DESC LIMIT 1)'
    sql_message_count_in_chain = '(SELECT COUNT(m.id) FROM messages m WHERE c.id = m.chain_id AND m.deleted = False)'
    sql = f'SELECT c.id, c.headline, {sql_message_count_in_chain}, {sql_last_sent_message} FROM chains c WHERE c.forum_id = :forum_id AND c.deleted = False GROUP BY c.id'
    return db.session.execute(sql, {'forum_id': forum_id}).fetchall()


def get_chains_info(chain_id):
    sql = 'SELECT c.headline, u.username FROM chains c, users u WHERE c.id = :chain_id AND u.id = c.creator_id'
    return db.session.execute(sql, {'chain_id': chain_id}).fetchall()


def add_new_chain(headline, message, creator_id, forum_id):
    sql = 'INSERT INTO chains (headline, creator_id, forum_id, deleted) VALUES (:headline, :creator_id, :forum_id, False) RETURNING id'
    chain_id = db.session.execute(
        sql, {'headline': headline, 'creator_id': creator_id, 'forum_id': forum_id}).fetchone()[0]
    ms.add_new_message(message, creator_id, chain_id)
    db.session.commit()
    return chain_id


def edit_chain_headline(chain_id, new_headline, writer_id):
    sql = 'UPDATE chains SET headline = :new_headline WHERE id = :chain_id AND creator_id = :writer_id'
    db.session.execute(sql, {'new_headline': new_headline,
                       'chain_id': chain_id, 'writer_id': writer_id})
    db.session.commit()


def delete_chain(chain_id, creator_id):
    sql = 'UPDATE chains SET deleted = True WHERE id = :chain_id AND creator_id = :creator_id'
    db.session.execute(sql, {'chain_id': chain_id, 'creator_id': creator_id})
    db.session.commit()

    sql_delete_messages = f'UPDATE messages SET deleted = True WHERE chain_id = :chain_id'
    db.session.execute(sql_delete_messages, {'chain_id': chain_id})
    db.session.commit()


def is_user_chain_creator(chain_id, user_id):
    sql = 'SELECT * FROM chains WHERE id = :chain_id AND creator_id = :user_id'
    access = db.session.execute(
        sql, {'chain_id': chain_id, 'user_id': user_id}).fetchall()
    if len(access) == 0:
        return False
    else:
        return True


def is_chain_deleted(chain_id):
    sql = 'SELECT deleted FROM chains where id = :chain_id'
    value = db.session.execute(sql, {'chain_id': chain_id}).fetchone()[0]
    return value
