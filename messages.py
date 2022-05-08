from db import db


def get_messages_info(chain_id):
    sql_likes = '(SELECT COUNT(l.id) FROM likes l WHERE m.id = l.message_id AND l.is_unlike = False)'
    sql_unlikes = '(SELECT COUNT(l.id) FROM likes l WHERE m.id = l.message_id AND l.is_unlike = True)'
    sql = f'SELECT m.id, m.message, u.username, TO_CHAR(m.sent_at, \'HH24:MI, Mon dd yyyy\'), {sql_likes}, {sql_unlikes} FROM messages m, users u WHERE m.chain_id = :chain_id AND u.id = m.writer_id AND m.deleted = False ORDER BY m.sent_at'
    return db.session.execute(sql, {'chain_id': chain_id}).fetchall()


def add_new_message(message, writer_id, chain_id):
    sql = 'INSERT INTO messages (message, writer_id, chain_id, deleted) VALUES (:message, :writer_id, :chain_id, False)'
    db.session.execute(
        sql, {'message': message, 'writer_id': writer_id, 'chain_id': chain_id})
    db.session.commit()


def delete_message(message_id, writer_id):
    sql = 'UPDATE messages SET deleted = True WHERE id = :message_id AND writer_id = :writer_id'
    db.session.execute(sql, {'message_id': message_id, 'writer_id': writer_id})
    db.session.commit()


def edit_message(message_id, new_message, writer_id):
    sql = 'UPDATE messages SET message = :new_message WHERE id = :message_id AND writer_id = :writer_id'
    db.session.execute(
        sql, {'new_message': new_message, 'message_id': message_id, 'writer_id': writer_id})
    db.session.commit()


def search_messages_with_word(word, user_id):
    sql_forum_id = '(SELECT f.id FROM forums f, chains c WHERE f.id = c.forum_id AND c.id = m.chain_id)'
    sql_writer_name = '(SELECT u.username FROM users u WHERE u.id = m.writer_id)'
    sql = f'''SELECT m.id, m.chain_id, {sql_forum_id}, {sql_writer_name}, m.message, TO_CHAR(m.sent_at, \'HH24:MI, Mon dd yyyy\'), m.deleted 
    FROM messages m
    WHERE m.deleted = False 
    AND (m.message LIKE :word1 OR m.message LIKE :word2 OR m.message LIKE :word3)
    AND m.chain_id IN 
    (SELECT c.id FROM chains c LEFT JOIN forums f ON f.id = c.forum_id WHERE f.is_secret = False OR f.id IN 
    (SELECT forum_id FROM has_access WHERE user_id = :user_id))'''

    messages = db.session.execute(
        sql, {'word1': word+'%', 'word2': '%'+word+'%', 'word3': '%'+word, 'user_id': user_id}).fetchall()
    return messages


def like_message(message_id, liker_id):
    sql = 'SELECT * FROM likes WHERE message_id = :message_id AND liker_id = :liker_id AND is_unlike = True'
    has_user_unliked = db.session.execute(
        sql, {'message_id': message_id, 'liker_id': liker_id}).fetchall()
    if len(has_user_unliked) == 0:
        sql = 'INSERT INTO likes (message_id, liker_id, is_unlike) VALUES (:message_id, :liker_id, False)'
        db.session.execute(
            sql, {'message_id': message_id, 'liker_id': liker_id})
        db.session.commit()
    else:
        sql = 'UPDATE likes SET is_unlike = False WHERE message_id = :message_id AND liker_id = :liker_id'
        db.session.execute(
            sql, {'message_id': message_id, 'liker_id': liker_id})
        db.session.commit()


def unlike_message(message_id, liker_id):
    sql = 'SELECT * FROM likes WHERE message_id = :message_id AND liker_id = :liker_id AND is_unlike = False'
    has_user_liked = db.session.execute(
        sql, {'message_id': message_id, 'liker_id': liker_id}).fetchall()
    if len(has_user_liked) == 0:
        sql = 'INSERT INTO likes (message_id, liker_id, is_unlike) VALUES (:message_id, :liker_id, False)'
        db.session.execute(
            sql, {'message_id': message_id, 'liker_id': liker_id})
        db.session.commit()
    else:
        sql = 'UPDATE likes SET is_unlike = True WHERE message_id = :message_id AND liker_id = :liker_id'
        db.session.execute(
            sql, {'message_id': message_id, 'liker_id': liker_id})
        db.session.commit()


def has_user_liked_message(message_id, liker_id):
    sql = 'SELECT * FROM likes WHERE message_id = :message_id AND liker_id = :liker_id AND is_unlike = False'
    message = db.session.execute(
        sql, {'message_id': message_id, 'liker_id': liker_id}).fetchall()
    if len(message) == 0:
        return True
    else:
        return False


def has_user_unliked_message(message_id, liker_id):
    sql = 'SELECT * FROM likes WHERE message_id = :message_id AND liker_id = :liker_id AND is_unlike = True'
    message = db.session.execute(
        sql, {'message_id': message_id, 'liker_id': liker_id}).fetchall()
    if len(message) == 0:
        return True
    else:
        return False


def is_user_message_writer(message_id, user_id):
    sql = 'SELECT * FROM messages WHERE id = :message_id AND writer_id = :user_id'
    access = db.session.execute(
        sql, {'message_id': message_id, 'user_id': user_id}).fetchall()
    if len(access) == 0:
        return False
    else:
        return True


def is_message_deleted(message_id):
    sql = 'SELECT deleted FROM messages where id = :message_id'
    value = db.session.execute(sql, {'message_id': message_id}).fetchone()[0]
    return value
