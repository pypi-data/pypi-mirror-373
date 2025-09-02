from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict


class GoogleDriveFileUpdateInfo(BaseModel):
    collection_id: str
    file_id: str
    file_name: str
    updated_time: datetime = Field(..., alias='updated_time')

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @classmethod
    def from_list(cls, data_list: List[dict]) -> List['GoogleDriveFileUpdateInfo']:
        return [cls(**item) for item in data_list]


class GoogleDriveFileUpdateResponse(BaseModel):
    file_id: str
    file_modified_time: datetime = Field(..., alias='file_modified_time')

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def to_dict(self) -> Dict:
        return {
            "file_id": self.file_id,
            "file_modified_time": self.file_modified_time.isoformat()
        }

    @classmethod
    def to_list(cls, objects: List['GoogleDriveFileUpdateResponse']) -> List[Dict]:
        return [obj.to_dict() for obj in objects]


if __name__ == '__main__':
    # 使用示例
    data_list = [
        {
            "collection_id": "1qk5maEqbxtTcr1tsAHawVduonPedpHV0",
            "file_id": "1cxJwtlTefxCFZvkMwaCaEOQEdi928__D",
            "file_name": "青年創業及啟動金貸款補貼息請領作業承貸金融機構應行注意事項問與答11101V6(紅字).pdf",
            "updated_time": "2024-07-10T01:27:57.031Z"
        },
        {
            "collection_id": "2qk5maEqbxtTcr1tsAHawVduonPedpHV0",
            "file_id": "2cxJwtlTefxCFZvkMwaCaEOQEdi928__D",
            "file_name": "另一個文件.pdf",
            "updated_time": "2024-07-11T14:30:00.000Z"
        }
    ]

    # 使用類方法處理列表
    file_info_list = GoogleDriveFileUpdateInfo.from_list(data_list)

    # 打印結果
    for file_info in file_info_list:
        print(file_info)
        print(file_info.model_dump())
        print("---")

    # 你也可以單獨處理一個字典
    single_data = data_list[0]
    single_file_info = GoogleDriveFileUpdateInfo(**single_data)
    print("單個對象:")
    print(single_file_info)
