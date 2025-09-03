import sys
import os
import json
from pathlib import Path


class PlayList():
    def __init__(self):
        super().__init__()
        self.list_dir = os.path.join(os.path.dirname(__file__),"Playlists")
        print("PL: ",self.list_dir)
        
        
        self.playlists = []
        self.get_playlists()
        #self.create_playlist()
        #self.add2Playlist()
    
    def get_playlists(self)->None:
        pl = Path( self.list_dir)
        
        for dir in pl.iterdir():
            print(dir)
            pl = str(dir).split("/")
            self.playlists.append(pl[len(pl)-1])
        
    
    def get_playlist_data(self,playlist: str)->dict:
        pl = playlist.lower()+".jspf"
        p = Path(self.list_dir)
        path = p / playlist / pl
        data = {}
        if os.path.exists(path):
            js = open(path,"r", encoding="utf-8")
            try:
                data = json.load(js)
            except json.JSONDecodeError as e:
                print(f'json error!\n check your playlist file at {e.lineno}')
                print(e.msg)
            
        else:
            print(path, " notfound")
        
        return data
    
#     def get_playlist_icon(self,playlist: str)->str:
#         path = Path(self.list_dir)
#         ip = path / playlist / "folder.svg"
#         
#         if os.path.exists(ip):
#             return str(ip)
#         else:
#             return ""
#     
#     def create_playlist(self):
#         
#         lists = self.parent.toolBox.count()
# 
#         for i, p in enumerate(self.playlists):
#             icon = self.get_playlist_icon(p)
#             if i < lists:
#                 self.parent.toolBox.setItemText(i,p)
#                 if len(icon) > 0:
#                     self.parent.toolBox.setItemIcon(i,QIcon(icon))
#             else:
#                 qlist = QListWidget(self)
#                 self.parent.toolBox.addItem(qlist,QIcon(icon),p)
#             
#             self.parent.toolBox.setCurrentIndex(i)
#             data = self.get_playlist_data(p)
#             if len(data) > 0:
#                 self.add2Playlist(p, data['playlist']['track'], self.parent.toolBox.currentWidget().children()[0]) 
#         
#         self.parent.toolBox.setCurrentIndex(0)
#     
#     def add2Playlist(self,pl: str, items: list, qlist: QListWidget):
#         path = f'{self.list_dir}/{pl}'
#         for item in items:
#             plItem = QListWidgetItem()
#             plItem.setText(item['title'])
#             #print(item['location'][0])
#             plItem.setData(3,item['location'][0])
#             plItem.setIcon(QIcon(f"{path}/{item['image']}"))
#             #print(type(qlist))
#             qlist.addItem(plItem)
        #plItem.setText("88.7 WSIE The Jazz Station")
        #plItem.setData(1,"http://streaming.siue.edu:8000/wsie")
        #plItem.setIcon(QIcon("Playlists/Jazz/WSIE_TheJazzStation.png"))
        
        