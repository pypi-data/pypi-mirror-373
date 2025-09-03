"""
micropyLMS.py 2025-06-24 v 1.0

Author: Brent Goode

Dependency lite and micropython friendly library for interacting with Lyrion 
Music Server (LMS, nee Squeezebox Server) systems
https://lyrion.org/reference/lyrion-music-server/
"""

import json
import requests

REPEAT_MODE = ["none", "song", "playlist"]
SHUFFLE_MODE = ["none", "song", "album"]

def build_url(host: str, prefix: str = 'http',port: str | int | None = '9000',
              username: str | None = '', password: str | None = '') -> str:
    """
    Helper function to build a server url
    Args:
        host: the IP address of the server on the local network
        prefix: either https or http depending
        port: port for server requests
        username and password: login credentials if needed
    Returns:
        string of the properly formatted url for the server
    """
    base_url = f"{prefix}://"
    
    base_url = f"{prefix}://"
    if username and password:
        base_url += f"{username}:{password}@"

    base_url += f"{host}:{port}/"
    return base_url

def core_query(server_url: str, *command, player: str = "") -> dict | None:
    """
    Generic query to interact with the LMS server.
    For how to structure commands see https://lyrion.org/reference/cli/using-the-cli/
    under the jsonrpc.js section and the command part of the body of the request
    Args:
        server_url: the url of the LMS server as returned by build_url()
        command: a string or list of strings containing CLI commands 
        player: 'playerid' of the LMS player the query is represented as coming from
    """
    query_data = {"id": "1", "method": "slim.request", "params": [player, command]}
    
    try:
        response = requests.get(server_url+'jsonrpc.js', json = query_data)
        if response.status_code != 200:
            print("Query failed, response code: %s Full message: %s",response)
            return None
        result_data = json.loads(response.content.decode(response.encoding))
    except Exception as exc:
        print(exc)
        return None
    try:
        result = result_data.get("result")
        if not isinstance(result, dict):
            print(f"Received invalid response: {result}")
            return None
        return result
    except KeyError:
        print(f"Received invalid response: {result_data}")
    return None

def get_players(server_url, image_scale: str | None = None):
    """Returns a list of Player objects for all players connected to server at server_url"""
    players: list[Player] = []
    data = core_query(server_url,"players", "status")
    if (data is None or not isinstance(data.get("players_loop"), list)):
        return []
    for player in data["players_loop"]:
        if not (isinstance(player, dict) and player.get("playerid") and player.get("name")):
            print(f"Received invalid response from LMS for player: {player}")
            continue
        new_player = Player(server_url, player["playerid"], image_scale)
        new_player.status_update()
        players.append(new_player)
    return players
    

def get_player(server_url, name: str | None = None, image_scale: str | None = None):
    """
    Returns a single player object with a case intensive match to name if found.
    If no name given or no match with name, returns the first player found.
    """
    player_list = get_players(server_url,image_scale)
    if name:
        players_found = []
        for player in player_list:
            if player.name.lower() == name.lower():
                players_found.append(player)
        if len(players_found) > 1:
            print(f'WARNING: More than one player named {name} found.')
        if players_found:
            return players_found[0]
        elif player_list:
            print(f'WARNING: No player named {name} found.')
            print(f'Returning {player_list[0].name} instead.')
            return player_list[0]
    else:
        if isinstance(player_list,list):
            return player_list[0]
    return None

class Player:
    """
    An object to hold information about and interaction methods for an LMS player

    Attributes
    ----------
    server_url: str
        url for the server that this player is a client of
    player_id: str
        'playerid' of the LMS player
    image_scale: str
        image scale text to be inserted into cover art url in scaled_image_url
    _status: dict
        dictionary where the raw results of a Player status query are held
    last_update_current_track:
        holds info on what the current track was during last update to allow 
        code that uses this library to know when the track has changed
    power: bool
        whether the player is on or not
    mode: str
        the playback state of the player: play, stop, or pause
    volume: int
        the player output volume from 0 to 100
    muting: bool
        whether the output of the player is muted
    duration: float
        length of the currently playing track in seconds
    time: float
        how far along in the current track (in seconds) the playback is
    track_id: str
        unique identifier of the currently track
    url: str
        unique url of the current track
    title: str
        title of the current track
    artist: str
        artist of the current track
    album: str
        album of the current track
    artwork_id: str
        unique id of the cover art  of the current track
    image_url: str
        url to load the image file of the cover art of the current track
    scaled_image_url: str
        url to load a scaled image file of the cover art of the current track
        scale set by Player __init__ arg image_scale
    current_index: int
        current track's index in the playlist
    current_track: dict
        full info on the current track
    remote: bool
        true if the current track is a remote stream
    remote_title: str
        title of the remote stream
    shuffle: int
        index of the current shuffle state in the list SHUFFLE_MODE
    repeat: int
        index of the current repeat state in the list REPEAT_MODE
    playlist_urls: list[dict]
        the urls for all tracks in the current playlist
    playlist_tracks: list[dict]
        full track information for all tracks in the current playlist

    Methods
    -------
    player_query() -> dict
        sends query to LMS serve from Player
    status_update()
        updates the stored player status status and attributes
    generate_image_url(image_url: str)
        combines server_url and image specific relative url
    set_volume(volume: str | int)
        Set volume level to value in range 0 to 100, or +/- an integer
    set_muting(mute: bool | int)
        sets the player mute state
    toggle_pause()
        if current playback start play, pauses, otherwise plays
    play()
        sends player the play command
    stop()
        sends player the stop command
    pause()
        sends player the pause command
    set_power(set_to: bool | int)
        sets the player power state
    load_url(url: str ,command: str = 'load')
        loads the give url into the current playlist
    load_playlist(playlist_ref: dict | list, command: str)
        loads the given item or playlist into the current playlist
    clear_playlist()
        removes all items from current playlist
    set_shuffle(shuffle: str)
        sets the shuffle state
    set_repeat(repeat: str)
        sets the repeat state
    """
    def __init__(self,server_url, player_id, image_scale):
        self.server_url = server_url
        self.player_id = player_id
        if image_scale:
            self.image_scale = image_scale
        else:
            self.image_scale = ''
        self._status = {}
        self.last_update_current_track = None
        
    @property
    def name(self) -> str:
        """the assigned name of the player as returned by the player itself"""
        return self._status.get('player_name')
    
    @property
    def power(self) -> bool:
        """the power state of the device"""
        return bool(self._status.get('power'))
        
    @property
    def mode(self) -> str | None:
        """the playback mode of the device. One of play, stop, or pause"""
        return self._status.get('mode')

    @property
    def volume(self) -> int | None:
        """volume of the player. integer from 0 to 100"""
        return abs(int(self._status.get('mixer volume',0)))
            
    @property
    def muting(self) -> bool:
        """true if volume is muted"""
        return str(self._status.get('mixer volume','')).startswith('-')

    @property
    def duration(self) -> float | None:
        """duration of current track in seconds"""
        return float(self.current_track.get('duration',0))        

    @property
    def time(self) -> float | None:
        """playback position of current track in seconds"""
        return float(self._status.get('time',0))

    @property
    def track_id(self) -> str | None:
        """id of current track"""
        if self.current_track:
            return self.current_track.get('id')
        return None
    
    @property
    def url(self) -> str | None:
        """unique id of current track"""
        if self.current_track:
            return self.current_track.get('url')
        return None
    
    @property
    def title(self) -> str:
        """title of track media"""
        if self.current_track:
            return self.current_track.get('title','')
        return ''

    @property
    def artist(self) -> str:
        """artist of current track"""
        if self.current_track:
            return self.current_track.get('artist','')
        return ''

    @property
    def album(self) -> str:
        """album of current track"""
        if self.current_track:
            return self.current_track.get('album','')
        return ''
    
    @property
    def artwork_id(self) -> str | None:
        """id for the current track's cover art"""
        if self.current_track:
            return self.current_track.get('artwork_track_id')
        return None
    
    @property
    def image_url(self) -> str:
        """url of current track's cover art"""
        if self.current_track:
            if self.current_track.get('artwork_url'):
                artwork_url = self.current_track["artwork_url"]
                if not artwork_url.startswith('http'):
                    artwork_url = self.generate_image_url('/'+artwork_url)
                artwork_url = '.'.join(artwork_url.split('.')[:-1])+'.png'
                return artwork_url
            return self.generate_image_url(f'/music/{self.artwork_id}/cover.png')
        return self.generate_image_url('/music/unknown/cover.png')

    @property
    def scaled_image_url(self) -> str:
        """
        url of cover art image with size scaled down to 240x240 by server
        NOTE: due to current LMS limitations images cannot be scaled up
        """
        if self.current_track:
            if self.current_track.get('artwork_url'):
                artwork_url = self.current_track["artwork_url"]
                if not artwork_url.startswith('http'):
                    artwork_url = self.generate_image_url('/'+artwork_url)
                artwork_url = '.'.join(artwork_url.split('.')[:-1])+f'{self.image_scale}.png'
                return artwork_url
            return self.generate_image_url(f'/music/{self.artwork_id}/cover{self.image_scale}.png')
        return self.generate_image_url(f'/music/unknown/cover{self.image_scale}.png')

    @property
    def current_index(self) -> int | None:
        """current track's index in the playlist"""
        if "playlist_cur_index" in self._status:
            return int(self._status.get('playlist_cur_index'))
        return None

    @property
    def current_track(self) -> dict | None:
        """full info on the current track"""
        if self.remote:
            return self._status.get('remoteMeta')
        else:
            if self.playlist and self.current_index is not None:
                return self.playlist[self.current_index]
        return None

    @property
    def remote(self) -> bool:
        """true if current track is a remote stream."""
        return bool(self._status.get('remote'))

    @property
    def remote_title(self) -> str | None:
        """title of the remote stream"""
        if self.current_track and 'remote_title' in self.current_track:
            return self.current_track.get('remote_title')
        return None

    @property
    def shuffle(self) -> str | None:
        """Return shuffle mode. May be 'none, 'song', or 'album'."""
        return self._status.get('playlist shuffle')

    @property
    def repeat(self) -> str | None:
        """Return repeat mode. May be 'none', 'song', or 'playlist'."""
        return self._status.get('playlist repeat')
        
    @property
    def playlist(self) -> list[dict] | None:
        """Return the current playlist."""
        return self._status.get('playlist_loop')

    @property
    def playlist_urls(self) -> list[dict] | None:
        """Return only the urls of the current playlist."""
        if not self.playlist:
            return None
        return [{'url': item['url']} for item in self.playlist]
    
    @property
    def playlist_tracks(self) -> int | None:
        """Return the current playlist length."""
        return int(self._status.get('playlist_tracks',0))
        
    @property
    def synced(self) -> bool:
        return bool(self._status.get('sync_master'))
    
    def player_query(self,*command):
        """Wraps core_query() to make it a Player method with Player details"""
        result = core_query(self.server_url,*command,player=self.player_id)
        if result == {}:
            return True
        else:
            return result

    def status_update(self): 
        """Updates Player status with fresh info"""
        response = self.player_query("status")
        if response is None:
            return False
        playlist_length = response['playlist_tracks']
        response = self.player_query('status','0',str(playlist_length),'tags:adJKlNux')
        if response:
            self._status = response
            return True
        else:
            print('ERROR: Received no response in status_update')
            return False
        
    def generate_image_url(self, image_url: str) -> str:
        """Adds the server_url to a relative image_url."""
        if self.server_url.endswith('/'):
            return self.server_url[:-1] + image_url
        else:
            return self.server_url + image_url

    def set_volume(self, volume: int | str):
        """Set volume level to value in range 0 to 100, or +/- an integer"""
        return self.player_query('mixer', 'volume', str(volume))

    def set_muting(self, mute: bool | int):
        """Sets mute (True, 1) or unmute (False, 0)"""
        mute = int(mute)
        return self.player_query('mixer', 'muting', mute)
        
    def toggle_pause(self):
        """
        Check current play/pause status and send the other as a command.
        Sends play if current status is stop
        """
        self.status_update()
        if self.mode == 'play':
            return self.player_query('pause')
        else:
            return self.player_query('play')

    def play(self):
        """Sends the play command"""
        return self.player_query("play")

    def stop(self):
        """Sends the stop command"""
        return self.player_query('stop')

    def pause(self):
        """Sends the pause command"""
        return self.player_query('pause')

    def set_power(self, set_to: bool | int):
        """Sets the player power to either on (True, 1) or off (False, 0)"""
        set_to = int(set_to)
        return self.player_query('power',set_to)

    def load_url(self, url: str, command: str = 'load'):
        """
        Play a specific track or stream by url. Useful for playing internet radio
        Args:
            url: playlist item url to load
            command: specifies how/where to load the url in the current playlist
                'play' or 'load' replaces current playlist with url
                'play_now' adds to url current spot in playlist
                'insert' adds url after the current item
                'add' adds url to end of playlist
        """
        index = self.current_index or 0
        if command in ['play_now', 'insert', 'add'] and self.playlist_urls:
            self.status_update()
            target_playlist = self.playlist_urls or []
            if command == 'add':
                target_playlist.append({'url': url})
            else:
                if command == 'insert':
                    index += 1
                target_playlist.insert(index, {'url': url})
        else:
            target_playlist = [{'url': url}]

        if command == 'play_now':
            self.load_playlist(target_playlist)
            return self.player_query('playlist', 'index', index)
        else:
            return self.player_query('playlist', command, url)

    def load_playlist(self, playlist_ref: dict | list, command: str = 'load'):
        """
        Play a playlist, of the sort return by the Player.playlist property.
        Args:
            playlist: a dictionary or list of dictionaries, which must each have a key called 'url'
            command: 'play' or 'load' - replace current playlist (default)
            command: 'insert' - adds next in playlist
            command: "add" - adds to end of playlist
        """
        if isinstance(playlist_ref,list):
            playlist = playlist_ref
        else:
            playlist = [playlist_ref]

        # remove non-playable items from the playlist
        playlist = [item for item in playlist if item.get('url')]

        if command == 'insert':
            for item in reversed(playlist):
                return self.load_url(item['url'], command)

        if command in ['play', 'load']:
            return self.load_url(playlist.pop(0)['url'], 'play')
            
        for item in playlist:
            return self.load_url(item['url'], 'add')
        
    def clear_playlist(self):
        return self.player_query('playlist', 'clear')

    def set_shuffle(self, shuffle: str):
        """Change shuffle mode to input value"""
        if shuffle in SHUFFLE_MODE:
            shuffle_int = SHUFFLE_MODE.index(shuffle)
            return self.player_query('playlist', 'shuffle', str(shuffle_int))
        else:
            print(f'Invalid shuffle mode: {shuffle}')
            return False

    def set_repeat(self, repeat: str):
        """change repeat mode to input value"""
        if repeat in REPEAT_MODE:
            repeat_int = REPEAT_MODE.index(repeat)
            return self.player_query('playlist', 'repeat', str(repeat_int))
        else:
            print(f'Invalid repeat mode: {repeat}')
            return False
    
    def unsync(self):
        """unsync player from all others"""
        return self.player_query("sync","-")

    def sync_to_other(self,other):
        """Syncs this player to one other player with given player_id (MAC address)"""
        return self.player_query("sync",other)

    def sync_to_all(self):
        """Syncs this player to all others that are clients to the same server"""
        player_list = get_players(self.server_url)
        sync_success = []
        for item in player_list:
            if self.name.lower() != item.name.lower():
                sync_success.append(self.player_query("sync",item.player_id))
        return all(player_list)
