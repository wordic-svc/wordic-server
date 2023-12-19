import uuid

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import DateTime

Base = declarative_base()

'''
폰트마스터
'''


class FnMaster(Base):
    __tablename__ = "TL_FN_MSTR"
    __table_args__ = {'comment': '폰트마스터'}

    id = Column(String, name="ID", primary_key=True, default=lambda: str(uuid.uuid4()), comment="아이디")
    reg_dt = Column("REG_DT", DateTime, default=datetime.utcnow, comment="등록일시")
    mdfcn_dt = Column("MDFCN_DT", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="수정일시")

    fnInfos = relationship("FnInfo", back_populates="fn_mstr")

'''
폰트정보
'''
class FnInfo(Base):
    __tablename__ = "TL_FN_INFO"
    __table_args__ = {'comment': '폰트정보'}

    id = Column(String, name="ID", primary_key=True, default=lambda: str(uuid.uuid4()), comment="아이디")
    fi_nm = Column(String, name="FILE_NM", comment="파일명")
    srch_id = Column(String, name="SRCH_ID", comment="검색 아이디")
    fn_nm = Column(String, name="FN_NM", comment="폰트명")
    fn_desc = Column(String, name="FN_DESC", comment="폰트설명")
    fn_thck = Column(String, name="FN_THCK", comment="폰트두께")
    etc_info = Column(String, name="ETC_INFO", comment="기타정보")
    ttf = Column(String, name="TTF", comment="TTF")
    otf = Column(String, name="OTF", comment="OTF")
    sppf = Column(String, name="SPPF", comment="판매가")
    reg_dt = Column("REG_DT", DateTime, default=datetime.utcnow, comment="등록일시")
    mdfcn_dt = Column("MDFCN_DT", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="수정일시")

    fn_mstr_id = Column("FN_MSTR", String, ForeignKey('TL_FN_MSTR.ID'))
    fn_mstr = relationship("FnMaster", back_populates="fnInfos")
