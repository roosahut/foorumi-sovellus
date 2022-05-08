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
    WHERE f.deleted = False AND f.is_secret = False OR f.id IN (SELECT forum_id FROM has_access WHERE user_id = :user_id)'''

    return db.session.execute(sql_all, {'user_id': user_id}).fetchall()


def has_user_forum_access(forum_id, user_id):
    sql_check_is_forum_secret = 'SELECT is_secret FROM forums WHERE id = :forum_id'
    is_secret = db.session.execute(sql_check_is_forum_secret, {'forum_id': forum_id}).fetchone()[0]
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


def get_chains_info_in_forum(forum_id):
    sql_last_sent_message = '(SELECT TO_CHAR(m.sent_at, \'HH24:MI, Mon dd yyyy\') FROM messages m WHERE m.chain_id = c.id AND m.deleted = False ORDER BY m.sent_at DESC LIMIT 1)'
    sql_message_count_in_chain = '(SELECT COUNT(m.id) FROM messages m WHERE c.id = m.chain_id AND m.deleted = False)'
    sql = f'SELECT c.id, c.headline, {sql_message_count_in_chain}, {sql_last_sent_message} FROM chains c WHERE c.forum_id = :forum_id AND c.deleted = False GROUP BY c.id'
    return db.session.execute(sql, {'forum_id': forum_id}).fetchall()


def get_messages_info(chain_id):
    sql_likes = '(SELECT COUNT(l.id) FROM likes l WHERE m.id = l.message_id AND l.is_unlike = False)'
    sql_unlikes = '(SELECT COUNT(l.id) FROM likes l WHERE m.id = l.message_id AND l.is_unlike = True)'
    sql = f'SELECT m.id, m.message, u.username, TO_CHAR(m.sent_at, \'HH24:MI, Mon dd yyyy\'), {sql_likes}, {sql_unlikes} FROM messages m, users u WHERE m.chain_id = :chain_id AND u.id = m.writer_id AND m.deleted = False ORDER BY m.sent_at'
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
    sql = 'INSERT INTO messages (message, writer_id, chain_id, deleted) VALUES (:message, :writer_id, :chain_id, False)'
    db.session.execute(
        sql, {'message': message, 'writer_id': writer_id, 'chain_id': chain_id})
    db.session.commit()


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

    sql_chains_in_forum = '(SELECT id FROM chains WHERE forum_id: forum_id)'
    sql_delete_chains = f'UPDATE chains SET deleted = True WHERE id = {sql_chains_in_forum}'
    db.session.execute(sql_delete_chains, {'forum_id': forum_id})
    db.session.commit()

    sql_messages_in_forum = f'(SELECT id FROM messages WHERE chain_id IN {sql_chains_in_forum})'
    sql_delete_messages = f'UPDATE messages SET deleted = True WHERE id = {sql_messages_in_forum}'
    db.session.execute(sql_delete_messages, {'forum_id': forum_id})
    db.session_execute


def delete_message(message_id, writer_id):
    sql = 'UPDATE messages SET deleted = True WHERE id = :message_id AND writer_id = :writer_id'
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

    sql_messages_in_chain = '(SELECT id FROM messages WHERE chain_id = :chain_id)'
    sql_delete_messages = f'UPDATE messages SET deleted = True WHERE id IN {sql_messages_in_chain}'
    db.session.execute(sql_delete_messages, {'chain_id': chain_id})
    db.session.commit()


def search_messages_with_word(word, user_id):
    sql_forum_id = '(SELECT f.id FROM forums f, chains c WHERE f.id = c.forum_id AND c.id = m.chain_id)'
    sql_writer_name = '(SELECT u.username FROM users u WHERE u.id = m.writer_id)'
    sql = f'''SELECT m.id, m.chain_id, {sql_forum_id}, {sql_writer_name}, m.message, TO_CHAR(m.sent_at, \'HH24:MI, Mon dd yyyy\'), m.deleted 
    FROM messages m 
    WHERE m.deleted = False AND (m.message LIKE :word1 OR m.message LIKE :word2 OR m.message LIKE :word3)'''
    messages = db.session.execute(
        sql, {'word1': word+'%', 'word2': '%'+word+'%', 'word3': '%'+word}).fetchall()
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


def is_user_chain_creator(chain_id, user_id):
    sql = 'SELECT * FROM chains WHERE id = :chain_id AND creator_id = :user_id'
    access = db.session.execute(sql, {'chain_id': chain_id, 'user_id': user_id}).fetchall()
    if len(access) == 0:
        return False
    else:
        return True


def is_user_message_writer(message_id, user_id):
    sql = 'SELECT * FROM messages WHERE id = :message_id AND writer_id = :user_id'
    access = db.session.execute(sql, {'message_id': message_id, 'user_id': user_id}).fetchall()
    if len(access) == 0:
        return False
    else:
        return True