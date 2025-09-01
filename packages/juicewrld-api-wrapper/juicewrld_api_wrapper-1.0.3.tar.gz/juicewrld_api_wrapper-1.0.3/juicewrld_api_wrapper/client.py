import requests
import time
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from urllib.parse import quote
from .models import Song, Artist, Album, Era, FileInfo, DirectoryInfo, SearchResult, Stats
from .exceptions import JuiceWRLDAPIError, RateLimitError, NotFoundError, AuthenticationError, ValidationError

class JuiceWRLDAPI:
    def __init__(self, base_url: str = "https://juicewrldapi.com", timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'JuiceWRLD-API-Wrapper/1.0.3',
            'Accept': 'application/json'
        })
        self.rate_limit_remaining = 100
        self.rate_limit_reset = time.time() + 60

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            
            if response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code == 404:
                raise NotFoundError("Resource not found")
            elif response.status_code == 401:
                raise AuthenticationError("Authentication required")
            elif response.status_code >= 400:
                raise JuiceWRLDAPIError(f"API error: {response.status_code} - {response.text}")
            
            return response.json()
        except requests.exceptions.RequestException as e:
            raise JuiceWRLDAPIError(f"Request failed: {str(e)}")

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._make_request('GET', endpoint, params=params)

    def _post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._make_request('POST', endpoint, json=data)

    def get_api_overview(self) -> Dict[str, Any]:
        data = self._get('/juicewrld/')
        return {
            'endpoints': data,
            'title': 'Juice WRLD API',
            'description': 'Comprehensive API for Juice WRLD discography and content',
            'version': '1.0.3'
        }

    def get_artists(self) -> List[Artist]:
        data = self._get('/juicewrld/artists/')
        return [Artist(**artist) for artist in data.get('results', [])]

    def get_artist(self, artist_id: int) -> Artist:
        data = self._get(f'/juicewrld/artists/{artist_id}/')
        return Artist(**data)

    def get_albums(self) -> List[Album]:
        data = self._get('/juicewrld/albums/')
        return [Album(**album) for album in data.get('results', [])]

    def get_album(self, album_id: int) -> Album:
        data = self._get(f'/juicewrld/albums/{album_id}/')
        return Album(**data)

    def get_songs(self, page: int = 1, category: Optional[str] = None, 
                  era: Optional[str] = None, search: Optional[str] = None, 
                  page_size: int = 20) -> Dict[str, Any]:
        params = {'page': page, 'page_size': page_size}
        if category:
            params['category'] = category
        if era:
            params['era'] = era
        if search:
            params['search'] = search
            
        data = self._get('/juicewrld/songs/', params=params)
        
        if 'results' in data:
            songs = []
            for song_data in data['results']:
                if isinstance(song_data, dict):
                    era_obj = Era(
                        id=song_data.get('era', {}).get('id', 0),
                        name=song_data.get('era', {}).get('name', 'Unknown'),
                        description=song_data.get('era', {}).get('description', ''),
                        time_frame=song_data.get('era', {}).get('time_frame', '')
                    )
                    
                    song = Song(
                        id=song_data.get('id', 0),
                        name=song_data.get('name', 'Unknown'),
                        original_key=song_data.get('original_key', ''),
                        category=song_data.get('category', 'unknown'),
                        era=era_obj,
                        track_titles=song_data.get('track_titles', []),
                        credited_artists=song_data.get('credited_artists', ''),
                        producers=song_data.get('producers', ''),
                        engineers=song_data.get('engineers', ''),
                        additional_information=song_data.get('additional_information', ''),
                        file_names=song_data.get('file_names', ''),
                        instrumentals=song_data.get('instrumentals', ''),
                        recording_locations=song_data.get('recording_locations', ''),
                        record_dates=song_data.get('record_dates', ''),
                        preview_date=song_data.get('preview_date', ''),
                        release_date=song_data.get('release_date', ''),
                        dates=song_data.get('dates', ''),
                        length=song_data.get('length', ''),
                        leak_type=song_data.get('leak_type', ''),
                        date_leaked=song_data.get('date_leaked', ''),
                        notes=song_data.get('notes', ''),
                        image_url=song_data.get('image_url', ''),
                        session_titles=song_data.get('session_titles', ''),
                        session_tracking=song_data.get('session_tracking', ''),
                        instrumental_names=song_data.get('instrumental_names', ''),
                        public_id=song_data.get('public_id', '')
                    )
                    songs.append(song)
            
            return {
                'results': songs,
                'count': data.get('count', 0),
                'next': data.get('next'),
                'previous': data.get('previous')
            }
        
        return data

    def get_song(self, song_id: int) -> Song:
        data = self._get(f'/juicewrld/songs/{song_id}/')
        return Song(**data)

    def get_eras(self) -> List[Era]:
        data = self._get('/juicewrld/eras/')
        return [Era(**era) for era in data.get('results', [])]

    def get_era(self, era_id: int) -> Era:
        data = self._get(f'/juicewrld/eras/{era_id}/')
        return Era(**data)

    def get_stats(self) -> Stats:
        data = self._get('/juicewrld/stats/')
        return Stats(**data)

    def get_categories(self) -> List[Dict[str, str]]:
        data = self._get('/juicewrld/categories/')
        return data.get('categories', [])

    def get_juicewrld_songs(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        params = {'page': page, 'page_size': page_size}
        return self._get('/juicewrld/player/songs/', params=params)

    def get_juicewrld_song(self, song_id: int) -> Dict[str, Any]:
        return self._get(f'/juicewrld/player/songs/{song_id}/')

    def play_juicewrld_song(self, song_id: int) -> Dict[str, Any]:
        try:
            song_data = self.get_juicewrld_song(song_id)
            if 'file' not in song_data:
                return {'error': 'Song file information not found', 'song_id': song_id, 'status': 'no_file_info'}
            
            file_url = song_data['file']
            if '/media/' in file_url:
                file_path = file_url.split('/media/')[-1]
            else:
                return {'error': 'Invalid file URL format', 'song_id': song_id, 'status': 'invalid_url'}
            
            possible_paths = [
                f"Compilation/1. Released Discography/{song_data.get('album', '')}/{song_data.get('title', '')}.mp3",
                f"Compilation/2. Unreleased Discography/{song_data.get('title', '')}.mp3",
                f"Snippets/{song_data.get('title', '')}/{song_data.get('title', '')}.mp4",
                f"Session Edits/{song_data.get('title', '')}.mp3"
            ]
            
            for test_path in possible_paths:
                try:
                    stream_url = f"{self.base_url}/juicewrld/files/download/?path={quote(test_path)}"
                    headers = {'Range': 'bytes=0-0'}
                    response = self.session.get(stream_url, headers=headers, timeout=5)
                    if response.status_code in [200, 206]:
                        return {
                            'status': 'success', 
                            'song_id': song_id, 
                            'stream_url': stream_url,
                            'file_path': test_path,
                            'content_type': response.headers.get('content-type', 'audio/mpeg')
                        }
                except:
                    continue
            
            stream_url = f"{self.base_url}/juicewrld/files/download/?path={quote(file_path)}"
            return {
                'status': 'file_not_found_but_url_provided', 
                'song_id': song_id, 
                'stream_url': stream_url,
                'file_path': file_path,
                'note': 'File may not exist at this path, but streaming URL is provided'
            }
                
        except Exception as e:
            return {'error': f'Request failed: {str(e)}', 'song_id': song_id, 'status': 'request_error'}

    def stream_audio_file(self, file_path: str) -> Dict[str, Any]:
        try:
            stream_url = f"{self.base_url}/juicewrld/files/download/?path={quote(file_path)}"
            
            headers = {'Range': 'bytes=0-0'}
            response = self.session.get(stream_url, headers=headers, timeout=self.timeout)
            
            if response.status_code in [200, 206]:
                return {
                    'status': 'success',
                    'stream_url': stream_url,
                    'file_path': file_path,
                    'content_type': response.headers.get('content-type', 'audio/mpeg'),
                    'content_length': response.headers.get('content-length'),
                    'supports_range': 'bytes' in response.headers.get('accept-ranges', '')
                }
            elif response.status_code == 404:
                return {'error': 'Audio file not found', 'file_path': file_path, 'status': 'file_not_found'}
            else:
                return {'error': f'HTTP {response.status_code}', 'file_path': file_path, 'status': 'http_error'}
                
        except Exception as e:
            return {'error': f'Request failed: {str(e)}', 'file_path': file_path, 'status': 'request_error'}

    def browse_files(self, path: str = '', search: Optional[str] = None) -> DirectoryInfo:
        params = {}
        if path:
            params['path'] = path
        if search:
            params['search'] = search
            
        data = self._get('/juicewrld/files/browse/', params=params)
        
        items = []
        for item in data.get('items', []):
            if item['type'] == 'file':
                try:
                    created = datetime.fromisoformat(item.get('created', '')) if item.get('created') else datetime.now()
                    modified = datetime.fromisoformat(item.get('modified', '')) if item.get('modified') else datetime.now()
                except (ValueError, TypeError):
                    created = datetime.now()
                    modified = datetime.now()
                
                items.append(FileInfo(
                    name=item.get('name', ''),
                    type=item.get('type', 'file'),
                    size=item.get('size', 0),
                    size_human=item.get('size_human', ''),
                    path=item.get('path', ''),
                    extension=item.get('extension', ''),
                    mime_type=item.get('mime_type', ''),
                    created=created,
                    modified=modified,
                    encoding=item.get('encoding')
                ))
            else:
                try:
                    modified = datetime.fromisoformat(item.get('modified', '')) if item.get('modified') else datetime.now()
                except (ValueError, TypeError):
                    modified = datetime.now()
                
                items.append(FileInfo(
                    name=item['name'],
                    type='directory',
                    size=0,
                    size_human='',
                    path=item['path'],
                    extension='',
                    mime_type='',
                    created=modified,
                    modified=modified,
                    encoding=None
                ))
        
        return DirectoryInfo(
            current_path=data.get('current_path', ''),
            path_parts=data.get('path_parts', []),
            items=items,
            total_files=data.get('total_files', 0),
            total_directories=data.get('total_directories', 0),
            search_query=data.get('search_query'),
            is_recursive_search=data.get('is_recursive_search', False)
        )

    def get_file_info(self, file_path: str) -> FileInfo:
        data = self._get('/juicewrld/files/info/', {'path': file_path})
        return FileInfo(**data)

    def download_file(self, file_path: str, save_path: Optional[str] = None) -> Union[bytes, str]:
        url = f"{self.base_url}/juicewrld/files/download/?path={quote(file_path)}"
        
        try:
            response = self.session.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            if save_path:
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return save_path
            else:
                return response.content
        except requests.exceptions.RequestException as e:
            raise JuiceWRLDAPIError(f"Download failed: {str(e)}")

    def get_cover_art(self, file_path: str) -> bytes:
        url = f"{self.base_url}/juicewrld/files/cover-art/?path={quote(file_path)}"
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            raise JuiceWRLDAPIError(f"Cover art retrieval failed: {str(e)}")

    def create_zip(self, file_paths: List[str]) -> bytes:
        data = {'paths': file_paths}
        response = self.session.post(
            f"{self.base_url}/juicewrld/files/zip-selection/",
            json=data,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.content

    def start_zip_job(self, file_paths: List[str]) -> str:
        data = {'paths': file_paths}
        response = self._post('/juicewrld/start-zip-job/', data)
        return response.get('job_id')

    def get_zip_job_status(self, job_id: str) -> Dict[str, Any]:
        return self._get(f'/juicewrld/zip-job-status/{job_id}/')

    def cancel_zip_job(self, job_id: str) -> bool:
        try:
            self._post(f'/juicewrld/cancel-zip-job/{job_id}/')
            return True
        except:
            return False

    def search_songs(self, query: str, category: Optional[str] = None, 
                    year: Optional[int] = None, tags: Optional[List[str]] = None,
                    limit: int = 50, offset: int = 0) -> SearchResult:
        page = (offset // limit) + 1 if limit > 0 else 1
        params = {'search': query, 'page_size': limit, 'page': page}
        if category:
            params['category'] = category
        if year:
            params['year'] = year
        if tags:
            params['tags'] = ','.join(tags)
            
        data = self._get('/juicewrld/songs/', params=params)
        
        songs = []
        for song_data in data.get('results', []):
            if isinstance(song_data, dict):
                era_obj = Era(
                    id=song_data.get('era', {}).get('id', 0),
                    name=song_data.get('era', {}).get('name', 'Unknown'),
                    description=song_data.get('era', {}).get('description', ''),
                    time_frame=song_data.get('era', {}).get('time_frame', '')
                )
                
                song = Song(
                    id=song_data.get('id', 0),
                    name=song_data.get('name', 'Unknown'),
                    original_key=song_data.get('original_key', ''),
                    category=song_data.get('category', 'unknown'),
                    era=era_obj,
                    track_titles=song_data.get('track_titles', []),
                    credited_artists=song_data.get('credited_artists', ''),
                    producers=song_data.get('producers', ''),
                    engineers=song_data.get('engineers', ''),
                    additional_information=song_data.get('additional_information', ''),
                    file_names=song_data.get('file_names', ''),
                    instrumentals=song_data.get('instrumentals', ''),
                    recording_locations=song_data.get('recording_locations', ''),
                    record_dates=song_data.get('record_dates', ''),
                    preview_date=song_data.get('preview_date', ''),
                    release_date=song_data.get('release_date', ''),
                    dates=song_data.get('dates', ''),
                    length=song_data.get('length', ''),
                    leak_type=song_data.get('leak_type', ''),
                    date_leaked=song_data.get('date_leaked', ''),
                    notes=song_data.get('notes', ''),
                    image_url=song_data.get('image_url', ''),
                    session_titles=song_data.get('session_titles', ''),
                    session_tracking=song_data.get('session_tracking', ''),
                    instrumental_names=song_data.get('instrumental_names', ''),
                    public_id=song_data.get('public_id', '')
                )
                songs.append(song)
        
        return SearchResult(
            songs=songs,
            total=data.get('count', 0),
            category=category,
            query_time='0ms'
        )

    def get_songs_by_category(self, category: str, page: int = 1, 
                            page_size: int = 20) -> Dict[str, Any]:
        return self.get_songs(page, category, page_size=page_size)





    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

