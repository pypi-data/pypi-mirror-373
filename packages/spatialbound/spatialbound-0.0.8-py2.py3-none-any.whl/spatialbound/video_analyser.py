# spatialbound/video_analyser.py
import os
import json
import mimetypes
import requests

# Define allowed video extensions if not already in config
ALLOWED_VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.wmv', '.mkv', '.webm', '.flv', '.mpeg', '.mpg', '.m4v', '.3gp']

class VideoAnalyser:
    def __init__(self, api_handler):
        self.api_handler = api_handler
    
    def upload_video(self, file_path):
        """
        Upload a video file to the API server.
        
        Args:
            file_path (str): Path to the video file on the local system.
            
        Returns:
            dict: Response containing the uploaded video URL.
        """
        # Check file existence
        if not os.path.isfile(file_path):
            return {"error": "File does not exist."}
        
        # Validate file extension
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension not in ALLOWED_VIDEO_EXTENSIONS:
            return {"error": f"Invalid video file extension. Allowed extensions are: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}"}
        
        # Determine content type explicitly
        content_type = mimetypes.guess_type(file_path)[0]
        if not content_type or not content_type.startswith('video/'):
            # Force a video content type based on common extensions
            content_type_map = {
                '.mp4': 'video/mp4',
                '.avi': 'video/x-msvideo',
                '.mov': 'video/quicktime',
                '.wmv': 'video/x-ms-wmv',
                '.mkv': 'video/x-matroska',
                '.webm': 'video/webm',
                '.flv': 'video/x-flv',
                '.mpeg': 'video/mpeg',
                '.mpg': 'video/mpeg',
                '.m4v': 'video/mp4',
                '.3gp': 'video/3gpp'
            }
            content_type = content_type_map.get(file_extension, 'video/mp4')  # Default to mp4
        
        endpoint = "/api/upload_video"
        
        # Upload the video file with explicit content type
        try:
            with open(file_path, 'rb') as file:
                # Use a tuple format that explicitly sets filename and content-type
                files = {'file': (os.path.basename(file_path), file, content_type)}
                return self.api_handler.make_authorised_request(endpoint, method='POST', files=files)
        except Exception as e:
            return {"error": f"Error uploading video: {str(e)}"}
    
    def analyse_video(self, video_url, user_prompt, fps):
        """
        Process a video file and convert it to structured data.
        
        Args:
            video_url (str): The URL of the previously uploaded video to process.
            user_prompt (str): The prompt for AI analysis.
            fps (int): Frames per second to extract.
            
        Returns:
            dict: A message and the extracted data.
        """
        # Validate inputs
        if not video_url:
            return {"error": "Video URL is required."}
        
        if not user_prompt:
            return {"error": "User prompt is required."}
        
        if fps <= 0 or fps > 25:
            return {"error": "FPS must be between 1 and 25."}
        
        # Ensure URL has a scheme - only prefixing with 'https://' if needed, not making up domains
        if not video_url.startswith(('http://', 'https://')):
            # Fix: Avoid using backslash in f-string
            fixed_url = video_url.replace('\\', '/')
            video_url = f"https://{fixed_url}"
        
        endpoint = "/api/convert_video"
        
        # Prepare form data
        form_data = {
            'video_url': video_url,
            'user_prompt': user_prompt,
            'fps': str(fps)  # Ensure fps is sent as a string
        }
        
        try:
            return self.api_handler.make_authorised_request(endpoint, method='POST', data=form_data)
        except Exception as e:
            return {"error": f"Error analyzing video: {str(e)}"}
    
    def search_video(self, query, video_url, limit=10, search_mode="semantic"):
        """
        Search for specific content within a video based on natural language queries.
        
        Args:
            query (str): Search query to find video moments.
            video_url (str): URL of the video to search.
            limit (int, optional): Maximum number of results to return (default 10).
            search_mode (str, optional): Search mode, "semantic" or "exact" (default "semantic").
            
        Returns:
            dict: Search results matching the query.
        """
        if not query:
            return {"error": "Search query is required."}
        
        if not video_url:
            return {"error": "Video URL is required."}
        
        # Ensure URL has a scheme
        if not video_url.startswith(('http://', 'https://')):
            # Fix: Avoid using backslash in f-string
            fixed_url = video_url.replace('\\', '/')
            video_url = f"https://{fixed_url}"
        
        endpoint = "/api/search_video"
        
        payload = {
            "query": query,
            "video_url": video_url,
            "limit": limit,
            "search_mode": search_mode
        }
        
        try:
            return self.api_handler.make_authorised_request(endpoint, method='POST', json=payload)
        except Exception as e:
            return {"error": f"Error searching video: {str(e)}"}
    
    def find_similarities(self, video_url, timestamp, limit=10, threshold=0.7):
        """
        Find moments in videos that are similar to a specific timestamp in a source video.
        
        Args:
            video_url (str): URL of the video to compare against database.
            timestamp (float): Timestamp in seconds to find similar moments.
            limit (int, optional): Maximum number of results to return (default 10).
            threshold (float, optional): Similarity threshold from 0.0 to 1.0 (default 0.7).
            
        Returns:
            dict: Similar moments found across videos.
        """
        if not video_url:
            return {"error": "Video URL is required."}
        
        if timestamp < 0:
            return {"error": "Timestamp must be non-negative."}
        
        if threshold < 0.1 or threshold > 1.0:
            return {"error": "Threshold must be between 0.1 and 1.0."}
        
        # Ensure URL has a scheme
        if not video_url.startswith(('http://', 'https://')):
            # Fix: Avoid using backslash in f-string
            fixed_url = video_url.replace('\\', '/')
            video_url = f"https://{fixed_url}"
        
        endpoint = "/api/find_similarities"
        
        payload = {
            "video_url": video_url,
            "timestamp": timestamp,
            "limit": limit,
            "threshold": threshold
        }
        
        try:
            return self.api_handler.make_authorised_request(endpoint, method='POST', json=payload)
        except Exception as e:
            return {"error": f"Error finding video similarities: {str(e)}"}
    
    def find_image_in_video(self, image_path, video_url, threshold=0.7):
        """
        Find an uploaded image within frames of a video, with automatic resizing 
        if needed to meet server upload size limits.
        
        Args:
            image_path (str): Path to the image file on the local system.
            video_url (str): URL of the video to search within.
            threshold (float, optional): Minimum similarity threshold (default 0.7).
            
        Returns:
            dict: Found timestamps and frames with similarity scores.
        """
        if not os.path.isfile(image_path):
            return {"error": "Image file does not exist."}
        
        if not video_url:
            return {"error": "Video URL is required."}
        
        if threshold < 0.1 or threshold > 1.0:
            return {"error": "Threshold must be between 0.1 and 1.0."}
        
        # Ensure URL has a scheme
        if not video_url.startswith(('http://', 'https://')):
            fixed_url = video_url.replace('\\', '/')
            video_url = f"https://{fixed_url}"
        
        endpoint = "/api/find_image_in_video"
        
        # Check file size - if over 4MB, we'll need to resize
        file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
        
        # Set up variables for potential resizing
        temp_file = None
        image_to_upload = image_path
        
        try:
            # If image is large, try to resize it
            if file_size_mb > 4:
                try:
                    # Import PIL only when needed
                    from PIL import Image
                    import tempfile
                    
                    # Create a temporary file
                    img_ext = os.path.splitext(image_path)[1].lower()
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=img_ext)
                    temp_filename = temp_file.name
                    temp_file.close()
                    
                    # Open and resize the image
                    with Image.open(image_path) as img:
                        # Calculate new dimensions while maintaining aspect ratio
                        # Start with 1024x1024 and reduce further if needed
                        max_dimension = 1024
                        width, height = img.size
                        if width > height:
                            new_width = max_dimension
                            new_height = int(height * (max_dimension / width))
                        else:
                            new_height = max_dimension
                            new_width = int(width * (max_dimension / height))
                        
                        # Resize the image
                        img = img.resize((new_width, new_height), Image.LANCZOS)
                        
                        # Save with compression
                        if img_ext in ['.jpg', '.jpeg']:
                            img.save(temp_filename, 'JPEG', quality=85, optimize=True)
                        elif img_ext == '.png':
                            img.save(temp_filename, 'PNG', optimize=True)
                        else:
                            # For other formats, convert to JPEG
                            img = img.convert('RGB')
                            temp_filename = temp_filename.rsplit('.', 1)[0] + '.jpg'
                            img.save(temp_filename, 'JPEG', quality=85, optimize=True)
                    
                    # Set the resized image as the one to upload
                    image_to_upload = temp_filename
                    new_size_mb = os.path.getsize(temp_filename) / (1024 * 1024)
                    
                    # If still too large, try more aggressive compression
                    if new_size_mb > 4:
                        with Image.open(temp_filename) as img:
                            # More aggressive resize
                            if width > height:
                                new_width = 800
                                new_height = int(height * (800 / width))
                            else:
                                new_height = 800
                                new_width = int(width * (800 / height))
                            
                            img = img.resize((new_width, new_height), Image.LANCZOS)
                            
                            # Higher compression
                            if img_ext in ['.jpg', '.jpeg'] or temp_filename.endswith('.jpg'):
                                img.save(temp_filename, 'JPEG', quality=70, optimize=True)
                            else:
                                img = img.convert('RGB')
                                img.save(temp_filename, 'JPEG', quality=70, optimize=True)
                    
                except ImportError:
                    # PIL not available, continue with original file
                    pass
                except Exception as e:
                    # Log but continue with original file
                    print(f"Warning: Could not resize image: {e}")
            
            # Determine content type for image
            image_content_type = mimetypes.guess_type(image_to_upload)[0]
            if not image_content_type or not image_content_type.startswith('image/'):
                # Force an image content type based on extension
                img_extension = os.path.splitext(image_to_upload)[1].lower()
                image_content_type_map = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.gif': 'image/gif',
                    '.bmp': 'image/bmp',
                    '.webp': 'image/webp',
                    '.tiff': 'image/tiff',
                    '.tif': 'image/tiff'
                }
                image_content_type = image_content_type_map.get(img_extension, 'image/jpeg')
            
            # Upload the image file
            with open(image_to_upload, 'rb') as image_file:
                files = {'image': (os.path.basename(image_to_upload), image_file, image_content_type)}
                form_data = {
                    'video_url': video_url,
                    'threshold': str(threshold)
                }
                
                response = self.api_handler.make_authorised_request(endpoint, method='POST', files=files, data=form_data)
                
                return response
        except Exception as e:
            return {"error": f"Error finding image in video: {str(e)}"}
        finally:
            # Clean up temporary file if it was created
            if temp_file is not None and os.path.exists(image_to_upload) and image_to_upload != image_path:
                try:
                    os.unlink(image_to_upload)
                except:
                    pass
                
    
    def analyze_video_location(self, video_url, fps=2):
        """
        Analyze a video to determine its geographical location.
        
        Args:
            video_url (str): URL of the video to analyze.
            fps (int, optional): Frames per second to extract (default 2).
            
        Returns:
            dict: Geolocation analysis results.
        """
        if not video_url:
            return {"error": "Video URL is required."}
        
        if fps <= 0 or fps > 5:
            return {"error": "FPS must be between 1 and 5."}
        
        # Ensure URL has a scheme
        if not video_url.startswith(('http://', 'https://')):
            # Fix: Avoid using backslash in f-string
            fixed_url = video_url.replace('\\', '/')
            video_url = f"https://{fixed_url}"
        
        endpoint = "/api/analyze_video_location"
        
        payload = {
            "video_url": video_url,
            "fps": fps
        }
        
        try:
            return self.api_handler.make_authorised_request(endpoint, method='POST', json=payload)
        except Exception as e:
            return {"error": f"Error analyzing video location: {str(e)}"}