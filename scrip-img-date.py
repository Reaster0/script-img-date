import datetime
import os
import piexif
import subprocess

#the directory path of your pictures and videos
directory_path = "./Camera"

def get_date_taken(filepath):
    _, extension = os.path.splitext(filepath)
    if extension.lower() in ('.mp4', '.3gp'):
        try:
            command = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_entries', 'format_tags=creation_time', '-i', filepath]
            output = subprocess.check_output(command, universal_newlines=True)
            lines = output.strip().split('\n')
            for line in lines:
              if len(line) > 0:
                try:
                  creation_time = line.strip().split(': ')[1]
                except:
                  continue
                if creation_time:
                    try:
                      date_taken = datetime.datetime.strptime(creation_time.replace('"', ''), '%Y-%m-%dT%H:%M:%S.%fZ')
                      return date_taken
                    except Exception as e:
                      continue
            raise Exception('No creation_time found')
        except Exception as e:
            print(f"Error processing video file '{filepath}': {str(e)}")
    return None

def set_file_modification_date(directory):
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            try:
                date_taken = get_date_taken(filepath)
                if date_taken:
                    # Set the file modification date
                   os.utime(filepath, (os.path.getatime(filepath), date_taken.timestamp()))
                   continue
                exif_data = piexif.load(filepath)
                if '0th' in exif_data and piexif.ImageIFD.DateTime in exif_data['0th']:
                    date_taken = exif_data['0th'][piexif.ImageIFD.DateTime]
                elif 'Exif' in exif_data and piexif.ExifIFD.DateTimeOriginal in exif_data['Exif']:
                    date_taken = exif_data['Exif'][piexif.ExifIFD.DateTimeOriginal]
                else:
                    continue

                # Convert the date string to a datetime object
                date_taken = datetime.datetime.strptime(date_taken.decode(), '%Y:%m:%d %H:%M:%S')

                # Set the file modification date
                os.utime(filepath, (os.path.getatime(filepath), date_taken.timestamp()))
                #print(f"Modified file '{filename}' with date '{date_taken}'")
            except Exception as e:
                print(f"Error processing file '{filename}': {str(e)}")

set_file_modification_date(directory_path)