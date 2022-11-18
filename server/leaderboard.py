""" Code for updating the leaderboard table. """
import hashlib

import humanhash

import server.schemas.leaderboard as leaderboard_db
import server.schemas.mturk as mturk_db
from server.lobby_consts import LobbyType
from server.schemas.google_user import GoogleUser
from server.username_word_list import USERNAME_WORDLIST


def GetLeaderboard(lobby_name: str = "", lobby_type: LobbyType = LobbyType.NONE):
    """Returns a list of the top 10 leaderboard entries."""
    query = leaderboard_db.Leaderboard.select()
    if len(lobby_name) > 0:
        query = query.where(leaderboard_db.Leaderboard.lobby_name == lobby_name)
    if lobby_type != LobbyType.NONE:
        query = query.where(leaderboard_db.Leaderboard.lobby_type == lobby_type)
    return query.order_by(leaderboard_db.Leaderboard.score.desc()).limit(10)


def UpdateLeaderboard(game_record):
    """Updates the leaderboard table with the latest score."""
    components = game_record.type.split("|")
    lobby_name = ""
    lobby_type = LobbyType.NONE
    if len(components) == 3:
        lobby_name = components[0]
        lobby_type = LobbyType(int(components[1]))
        components[2]
    else:
        game_record.type
    if game_record.score > 0 and lobby_name != "" and lobby_type != LobbyType.NONE:
        leaderboard_entry = leaderboard_db.Leaderboard.create(
            time=game_record.end_time,
            score=game_record.score,
            lobby_name=lobby_name,
            lobby_type=lobby_type,
        )
        if lobby_type in [LobbyType.MTURK]:
            leaderboard_entry.mturk_leader = game_record.leader
            leaderboard_entry.mturk_follower = game_record.follower
        elif lobby_type in [LobbyType.GOOGLE]:
            leaderboard_entry.google_leader = game_record.google_leader
            leaderboard_entry.google_follower = game_record.google_follower
        leaderboard_entry.save()
    # If there are now more than 10 entries, delete the one with the lowest score.
    query = leaderboard_db.Leaderboard.select()
    if len(lobby_name) > 0:
        query = query.where(leaderboard_db.Leaderboard.lobby_name == lobby_name)
    if lobby_type != LobbyType.NONE:
        query = query.where(leaderboard_db.Leaderboard.lobby_type == lobby_type)
    if query.count() > 10:
        lowest_entry = query.order_by(leaderboard_db.Leaderboard.score.asc()).get()
        lowest_entry.delete_instance()


def LookupUsername(worker):
    """Returns the username for a given worker."""
    username_select = leaderboard_db.Username.select().where(
        leaderboard_db.Username.worker == worker
    )
    if username_select.count() == 0:
        return None
    return username_select.get().username


def UsernameFromHashedGoogleUserId(user_id_shasum):
    """Returns a user's username from their hashed google account ID."""
    google_user = (
        GoogleUser.select().where(GoogleUser.hashed_google_id == user_id_shasum).get()
    )
    username_select = leaderboard_db.Username.select().where(
        leaderboard_db.Username.user == google_user
    )
    if username_select.count() == 0:
        return None
    return username_select.get().username


def LookupUsernameFromUser(user):
    """Returns the username for a given user."""
    username_select = leaderboard_db.Username.select().where(
        leaderboard_db.Username.worker == user.worker
    )
    if username_select.count() == 0:
        return None
    return username_select.get().username


def LookupUsernameFromId(worker_id):
    md5sum = hashlib.md5(worker_id.encode("utf-8")).hexdigest()
    return LookupUsernameFromMd5sum(md5sum)


def LookupUsernameFromMd5sum(worker_id_md5sum):
    worker_select = mturk_db.Worker.select().where(
        mturk_db.Worker.hashed_id == worker_id_md5sum
    )
    if worker_select.count() == 0:
        return None
    return LookupUsername(worker_select.get())


def SetUsername(worker, username):
    """Sets the username for a given worker."""
    username_select = leaderboard_db.Username.select().where(
        leaderboard_db.Username.worker == worker
    )
    if username_select.count() == 0:
        username_entry = leaderboard_db.Username.create(
            username=username, worker=worker
        )
        username_entry.save()
    else:
        username_select.get().username = username
        username_select.get().save()


def SetGoogleUsername(user_id_shasum, username):
    """Sets the username for a given google user."""
    google_user = (
        GoogleUser.select().where(GoogleUser.hashed_google_id == user_id_shasum).get()
    )
    username_select = leaderboard_db.Username.select().where(
        leaderboard_db.Username.user == google_user
    )
    if username_select.count() == 0:
        username_entry = leaderboard_db.Username.create(
            username=username, user=google_user
        )
        username_entry.save()
    else:
        username_select.get().username = username
        username_select.get().save()


def SetDefaultUsername(worker):
    """Uses humanhash to generate a default 2 word username based on the worker's hashed_id. Adds it to the Username table."""
    hasher = humanhash.HumanHasher(wordlist=USERNAME_WORDLIST)
    username = hasher.humanize(worker.hashed_id, words=2)
    SetUsername(worker, username)


def SetDefaultGoogleUsername(user_id_shasum):
    """Uses humanhash to generate a default 2 word username based on the worker's hashed_id. Adds it to the Username table."""
    hasher = humanhash.HumanHasher(wordlist=USERNAME_WORDLIST)
    username = hasher.humanize(user_id_shasum, words=2)
    SetGoogleUsername(user_id_shasum, username)
