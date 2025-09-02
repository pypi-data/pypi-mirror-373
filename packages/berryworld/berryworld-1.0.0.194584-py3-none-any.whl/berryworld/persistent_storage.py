import os
import time
import shutil
import pandas as pd
from pathlib import Path
from datetime import datetime


class PersistentStorage:
    """ Connect to Persistent Storage """

    def __init__(self, base=None):
        """ Workout the root and the base path
        :param base: Root folder to be used
        """
        if os.name == 'nt':
            root = os.getcwd()
        else:
            root = 'storage'

        self.base_path = os.path.join(os.getcwd(), root)
        if not self.if_exists(self.base_path):
            raise ValueError(f"The persistent storage path: {self.base_path} is not properly set up.")

        if base is not None:
            self.base_path = os.path.join(os.getcwd(), root, base)
            if not self.if_exists(self.base_path):
                try:
                    os.makedirs(self.base_path, exist_ok=True)
                except:
                    raise ValueError(f"Couldn't create storage path: {self.base_path}.")

    def format_path(self, path_, sub_path=None):
        """ Format the path
        :param path_: Path to be formatted
        :param sub_path: Sub path to be added to the path
        """
        if self.base_path in path_:
            format_path = path_
        else:
            format_path = os.path.join(self.base_path, path_)

        if sub_path is not None:
            format_path = os.path.join(format_path, sub_path)

        return format_path

    def if_exists(self, path_='.'):
        """ Check if the path exists
        :param path_: Path to be checked
        """
        path_ = os.path.join(self.base_path, str(self.format_path(path_)))
        obj = Path(path_)
        status = obj.exists()
        return status

    def return_base_path(self):
        """ Return the base path """
        return self.base_path

    def return_input_path(self, path_):
        """ Return the input path
        :param path_: Path to be returned
        """
        path_ = self.format_path(path_)
        return path_

    def create_folder(self, path_='.'):
        """ Create a folder
        :param path_: Path to create the folder
        """
        created = True
        folder_path = os.path.join(self.base_path, str(self.format_path(path_)))
        try:
            Path(folder_path).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(e)
            created = False
        return created

    def list_folders(self, path_='.'):
        """ List all the folders in the path
        :param path_: Path to list the folders
        """
        folder_path = os.path.join(self.base_path, str(self.format_path(path_)))
        try:
            if self.if_exists(folder_path):
                folders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
                folders.sort()
            else:
                folders = []
        except Exception as e:
            raise Exception(e)

        return folders

    def create_file(self, data_, path_='.', file_name=None):
        """ Create a file
        :param data_: Data to be written to the file
        :param path_: Path to create the file
        :param file_name: Name of the file to be created
        """
        created = True
        folder_path = os.path.join(self.base_path, str(self.format_path(path_)))
        if file_name is None:
            file_path = os.path.join(folder_path, datetime.now().strftime("%H_%M_%S_%f"))
        else:
            file_path = os.path.join(folder_path, file_name)

        try:
            if type(data_) == bytes:
                with open(file_path, 'wb') as f:
                    f.write(data_)
                    f.close()
            else:
                with open(file_path, 'w') as f:
                    f.write(data_)
                    f.close()
        except Exception as e:
            print(e)
            created = False

        return created

    def list_files(self, path_='.'):
        """ List all the files in the path
        :param path_: Path to list the files
        """
        folder_path = os.path.join(self.base_path, str(self.format_path(path_)))
        try:
            if self.if_exists(folder_path):
                files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
                files.sort()
            else:
                files = []
        except Exception as e:
            raise Exception(e)

        return files

    def move_files(self, source_folder, target_folder, source_files=None, move_all=False):
        """ Move files from source to target folder
        :param source_folder: Source folder
        :param target_folder: Target folder
        :param source_files: Files to be moved
        :param move_all: Move all files
        """
        source_path = str(self.format_path(source_folder))
        target_path = str(self.format_path(target_folder))
        if source_files is None:
            source_files = self.list_files(source_folder)
            all_source_files = source_files
            i = 0
            while len(source_files) > 0 and i <= 5:
                for f in source_files:
                    incoming_file_path = os.path.join(source_path, f)
                    received_file_path = os.path.join(target_path, f)
                    shutil.move(incoming_file_path, received_file_path)

                time.sleep(5)
                source_files = self.list_files(source_folder)
                all_source_files.extend(source_files)
                if not move_all:
                    i += 1

        else:
            all_source_files = source_files
            for f in source_files:
                incoming_file_path = os.path.join(source_path, f)
                received_file_path = os.path.join(target_path, f)
                shutil.move(incoming_file_path, received_file_path)

        target_files = [f for f in os.listdir(target_path) if os.path.isfile(os.path.join(target_path, f))]
        moved_files = list(set(all_source_files) & set(target_files))
        moved_files.sort()
        return moved_files

    def move_file(self, source_file_path, target_file_path):
        """ Move a file from source to target path
        :param source_file_path: Source file path
        :param target_file_path: Target file path
        """
        try:
            if self.if_exists(source_file_path) & Path(source_file_path).is_file():
                shutil.move(source_file_path, target_file_path)
            return True
        except Exception as e:
            print(e)
            return False

    def get_folder_creation(self, path_):
        """ Get the create time of the file
        :param path_: Path to get the create time
        """
        path_ = str(self.format_path(path_))
        if self.if_exists(path_):
            create_time = pd.to_datetime(time.ctime(os.path.getctime(path_)))
            return create_time
        else:
            return None

    def delete_folder(self, path_):
        """ Delete a folder
        :param path_: Path to delete the folder
        """
        folder_path = os.path.join(self.base_path, str(self.format_path(path_)))
        delete = True
        try:
            if self.if_exists(folder_path):
                shutil.rmtree(folder_path)
        except Exception as e:
            print(e)
            delete = False

        return delete

    def delete_file(self, path_):
        """ Delete a file
        :param path_: Path to delete the file
        """
        file_path = os.path.join(self.base_path, str(self.format_path(path_)))
        delete = True
        try:
            if self.if_exists(file_path) & Path(path_).is_file():
                os.remove(file_path)
        except Exception as e:
            print(e)
            delete = False

        return delete

    def get_file_creation(self, path_):
        """ Get when a file was created
        :param path_: Path to the file
        """
        path_ = str(self.format_path(path_))
        if self.if_exists(path_):
            create_time = pd.to_datetime(time.ctime(os.path.getctime(path_)))
            return create_time
        else:
            return None

    def delete_older_files(self, path_, date):
        """ Archive the files
        :param path_: Path to the files
        :param date: Date to archive the files
        """
        file_path = os.path.join(self.base_path, str(self.format_path(path_)))

        files_to_remove = [file for file in os.listdir(file_path) if
                           date >= self.get_file_creation(os.path.join(file_path, file))]
        for file in files_to_remove:
            self.delete_file(os.path.join(file_path, file))
