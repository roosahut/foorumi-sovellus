from db import db


def get_all_forums():
    sql = 'SELECT id, name FROM forums ORDER BY name'
    return db.session.execute(sql).fetchall()


def get_forums_info():
    sql_get_chain_count_in_forum = '(SELECT COUNT(c.id) FROM chains c WHERE f.id = c.forum_id AND c.deleted = False)'
    sql_message_count_in_forum = '(SELECT COUNT(m.id) FROM messages m, chains c WHERE c.id = m.chain_id AND f.id = c.forum_id AND c.deleted = False GROUP BY f.id)'
    sql_get_last_sent_message = '(SELECT TO_CHAR(m.sent_at, \'HH24:MI, Mon dd yyyy\') FROM messages m LEFT JOIN chains c ON c.id = m.chain_id WHERE f.id = c.forum_id AND c.deleted = False ORDER BY m.sent_at DESC LIMIT 1)'
    sql_all = f'SELECT f.id, f.name, {sql_get_chain_count_in_forum}, {sql_message_count_in_forum}, {sql_get_last_sent_message} FROM forums f WHERE f.deleted = False'
    return db.session.execute(sql_all).fetchall()


def get_forum_name(forum_id):
    sql = 'SELECT name FROM forums WHERE id = :forum_id'
    return db.session.execute(sql, {'forum_id': forum_id}).fetchone()


def get_chains_info_in_forum(forum_id):
    sql_last_sent_message = '(SELECT TO_CHAR(m.sent_at, \'HH24:MI, Mon dd yyyy\') FROM messages m WHERE m.chain_id = c.id ORDER BY m.sent_at DESC LIMIT 1)'
    sql_message_count_in_chain = '(SELECT COUNT(m.id) FROM messages m WHERE c.id = m.chain_id)'
    sql = f'SELECT c.id, c.headline, {sql_message_count_in_chain}, {sql_last_sent_message} FROM chains c WHERE c.forum_id = :forum_id AND c.deleted = False GROUP BY c.id'
    return db.session.execute(sql, {'forum_id': forum_id}).fetchall()


def get_messages_info(chain_id):
    sql = 'SELECT m.id, m.message, u.username, TO_CHAR(m.sent_at, \'HH24:MI, Mon dd yyyy\') FROM messages m, users u WHERE m.chain_id = :chain_id AND u.id = m.writer_id ORDER BY m.sent_at'
    return db.session.execute(sql, {'chain_id': chain_id}).fetchall()


def get_chains_info(chain_id):
    sql = 'SELECT c.headline, u.username FROM chains c, users u WHERE c.id = :chain_id AND u.id = c.creator_id'
    return db.session.execute(sql, {'chain_id': chain_id}).fetchall()


def add_new_chain(headline, message, creator_id, forum_id):
    sql = 'INSERT INTO chains (headline, creator_id, forum_id, deleted) VALUES (:headline, :creator_id, :forum_id, False) RETURNING id'
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
    sql = 'INSERT INTO forums (name, creator_id, deleted) VALUES (:name, :creator_id, False) RETURNING id'
    forum_id = db.session.execute(
        sql, {'name': name, 'creator_id': creator_id}).fetchone()[0]
    db.session.commit()
    return forum_id


def delete_forum(forum_id):
    sql = 'UPDATE forums SET deleted = True WHERE id = :forum_id'
    db.session.execute(sql, {'forum_id': forum_id})
    db.session.commit()


def delete_message(message_id, writer_id):
    sql = 'DELETE FROM messages WHERE id = :message_id AND writer_id = :writer_id'
    db.session.execute(sql, {'message_id': message_id, 'writer_id': writer_id})
    db.session.commit()


def edit_message(message_id, new_message, writer_id):
    sql = 'UPDATE messages SET message = :new_message WHERE id = :message_id AND writer_id = :writer_id'
    db.session.execute(
        sql, {'new_message': new_message, 'message_id': message_id, 'writer_id': writer_id})
    db.session.commit()


def edit_chain_headline(chain_id, new_headline, writer_id):
    sql = 'UPDATE chains SET headline = :new_headline WHERE id = :chain_id AND creator_id = :writer_id'
    db.session.execute(sql, {'new_headline': new_headline,
                       'chain_id': chain_id, 'writer_id': writer_id})
    db.session.commit()


def delete_chain(chain_id, creator_id):
    sql = 'UPDATE chains SET deleted = True WHERE id = :chain_id AND creator_id = :creator_id'
    db.session.execute(sql, {'chain_id': chain_id, 'creator_id': creator_id})
    db.session.commit()


def find_messages_with_word(word):
    sql_forum_id = '(SELECT f.id FROM forums f, chains c WHERE f.id = c.forum_id AND c.id = m.chain_id)'
    sql_writer_name = '(SELECT u.username FROM users u WHERE u.id = m.writer_id)'
    sql = f'SELECT m.id, m.chain_id, {sql_forum_id}, {sql_writer_name}, m.message, TO_CHAR(m.sent_at, \'HH24:MI, Mon dd yyyy\') FROM messages m WHERE m.message LIKE :word1 OR m.message LIKE :word2 OR m.message LIKE :word3'
    messages = db.session.execute(sql, {'word1': word+'%', 'word2': '%'+word+'%', 'word3': '%'+word}).fetchall()
    return messages