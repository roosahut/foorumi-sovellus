from db import db


def get_all_forums():
    sql = 'SELECT id, name FROM forums ORDER BY name'
    return db.session.execute(sql).fetchall()


def get_forums_info():
    sql_get_chain_count_in_forum = '(SELECT COUNT(c.id) FROM chains c WHERE f.id = c.forum_id)'
    sql_message_count_in_forum = '(SELECT COUNT(m.id) FROM messages m, chains c WHERE c.id = m.chain_id AND f.id = c.forum_id GROUP BY f.id)'
    sql_get_last_sent_message = '(SELECT TO_CHAR(m.sent_at, \'HH24:MI, Mon dd yyyy\') FROM messages m LEFT JOIN chains c ON c.id = m.chain_id WHERE f.id = c.forum_id ORDER BY m.sent_at DESC LIMIT 1)'
    sql_all = f'SELECT f.id, f.name, {sql_get_chain_count_in_forum}, {sql_message_count_in_forum}, {sql_get_last_sent_message} FROM forums f'
    return db.session.execute(sql_all).fetchall()


def get_forum_name(forum_id):
    sql = 'SELECT name FROM forums WHERE id = :forum_id'
    return db.session.execute(sql, {'forum_id': forum_id}).fetchone()


def get_chains_info_in_forum(forum_id):
    sql_last_sent_message = '(SELECT TO_CHAR(m.sent_at, \'HH24:MI, Mon dd yyyy\') FROM messages m WHERE m.chain_id = c.id ORDER BY m.sent_at DESC LIMIT 1)'
    sql_message_count_in_chain = '(SELECT COUNT(m.id) FROM messages m WHERE c.id = m.chain_id)'
    sql = f'SELECT c.id, c.headline, {sql_message_count_in_chain}, {sql_last_sent_message} FROM chains c WHERE c.forum_id = :forum_id GROUP BY c.id'
    return db.session.execute(sql, {'forum_id': forum_id}).fetchall()


def get_messages_info(chain_id):
    sql = 'SELECT m.id, m.message, u.username, TO_CHAR(m.sent_at, \'HH24:MI, Mon dd yyyy\') FROM messages m, users u WHERE m.chain_id = :chain_id AND u.id = m.writer_id ORDER BY m.sent_at'
    return db.session.execute(sql, {'chain_id': chain_id}).fetchall()


def get_chains_info(chain_id):
    sql = 'SELECT c.headline, u.username FROM chains c, users u WHERE c.id = :chain_id AND u.id = c.creator_id'
    return db.session.execute(sql, {'chain_id': chain_id}).fetchall()


def add_new_chain(headline, message, creator_id, forum_id):
    sql = 'INSERT INTO chains (headline, creator_id, forum_id) VALUES (:headline, :creator_id, :forum_id) RETURNING id'
    chain_id = db.session.execute(
        sql, {'headline': headline, 'creator_id': creator_id, 'forum_id': forum_id}).fetchone()[0]
    add_new_message(message, creator_id, chain_id)
    db.session.commit()
    return chain_id


def add_new_message(message, writer_id, chain_id):
    sql = 'INSERT INTO messages (message, writer_id, chain_id) VALUES (:message, :writer_id, :chain_id)'
    db.session.execute(
        sql, {'message': message, 'writer_id': writer_id, 'chain_id': chain_id})
    db.session.commit()


def add_new_forum(name, creator_id):
    sql = 'INSERT INTO forums (name, creator_id) VALUES (:name, :creator_id) RETURNING id'
    forum_id = db.session.execute(
        sql, {'name': name, 'creator_id': creator_id}).fetchone()[0]
    db.session.commit()
    return forum_id


def delete_message(message_id):
    sql = 'DELETE FROM messages WHERE id = :message_id'
    db.session.execute(sql, {'message_id': message_id})
    db.session.commit()


def edit_message(message_id, new_message):
    sql = 'UPDATE messages SET message = :new_message WHERE id = :message_id'
    db.session.execute(
        sql, {'new_message': new_message, 'message_id': message_id})
    db.session.commit()
