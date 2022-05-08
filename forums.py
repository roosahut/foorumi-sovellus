from db import db
import users


def get_all_forums():
    sql = 'SELECT id, name FROM forums ORDER BY name'
    return db.session.execute(sql).fetchall()


def get_forums_info():
    sql_get_chain_count_in_forum = '(SELECT COUNT(c.id) FROM chains c WHERE f.id = c.forum_id AND c.deleted = False)'

    sql_message_count_in_forum = '''(SELECT COUNT(m.id) FROM messages m, chains c 
    WHERE c.id = m.chain_id AND f.id = c.forum_id AND c.deleted = False AND m.deleted = False GROUP BY f.id)'''

    sql_get_last_sent_message = '''(SELECT TO_CHAR(m.sent_at, \'HH24:MI, Mon dd yyyy\') 
    FROM messages m LEFT JOIN chains c ON c.id = m.chain_id 
    WHERE f.id = c.forum_id AND c.deleted = False AND m.deleted = False 
    ORDER BY m.sent_at DESC LIMIT 1)'''

    user_id = users.user_id()
    sql_all = f'''SELECT f.id, f.name, {sql_get_chain_count_in_forum}, {sql_message_count_in_forum}, {sql_get_last_sent_message} 
    FROM forums f 
    WHERE f.deleted = False AND (f.is_secret = False OR f.id IN (SELECT forum_id FROM has_access WHERE user_id = :user_id))'''

    return db.session.execute(sql_all, {'user_id': user_id}).fetchall()


def has_user_forum_access(forum_id, user_id):
    sql_check_is_forum_secret = 'SELECT is_secret FROM forums WHERE id = :forum_id'
    is_secret = db.session.execute(sql_check_is_forum_secret, {
                                   'forum_id': forum_id}).fetchone()[0]
    if not is_secret:
        return True
    else:
        sql = 'SELECT * FROM has_access WHERE forum_id = :forum_id AND user_id = :user_id'
        access = db.session.execute(
            sql, {'forum_id': forum_id, 'user_id': user_id}).fetchall()
        if len(access) == 0:
            return False
        else:
            return True


def get_forum_name(forum_id):
    sql = 'SELECT name FROM forums WHERE id = :forum_id'
    return db.session.execute(sql, {'forum_id': forum_id}).fetchone()


def add_new_forum(name, creator_id, is_secret):
    sql = 'INSERT INTO forums (name, creator_id, deleted, is_secret) VALUES (:name, :creator_id, False, :is_secret) RETURNING id'
    forum_id = db.session.execute(
        sql, {'name': name, 'creator_id': creator_id, 'is_secret': is_secret}).fetchone()[0]
    db.session.commit()
    return forum_id


def add_access_to_secret_forum(forum_id, user_id):
    sql = f'INSERT INTO has_access (forum_id, user_id) VALUES (:forum_id, :user_id)'
    db.session.execute(sql, {'forum_id': forum_id, 'user_id': user_id})
    db.session.commit()


def delete_forum(forum_id):
    sql = 'UPDATE forums SET deleted = True WHERE id = :forum_id'
    db.session.execute(sql, {'forum_id': forum_id})
    db.session.commit()

    sql_chains_in_forum = '(SELECT id FROM chains WHERE forum_id = :forum_id)'
    sql_delete_chains = f'UPDATE chains SET deleted = True WHERE forum_id = :forum_id'
    db.session.execute(sql_delete_chains, {'forum_id': forum_id})
    db.session.commit()

    sql_delete_messages = f'UPDATE messages SET deleted = True WHERE chain_id IN {sql_chains_in_forum}'
    db.session.execute(sql_delete_messages, {'forum_id': forum_id})
    db.session.commit()


def is_forum_deleted(forum_id):
    sql = 'SELECT deleted FROM forums where id = :forum_id'
    value = db.session.execute(sql, {'forum_id': forum_id}).fetchone()[0]
    return value
