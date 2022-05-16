import uuid

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import DateTime

Base = declarative_base()

'''
단어마스터
'''
class FnWord(Base):
    __tablename__ = "TL_WORD"
    __table_args__ = {'comment': '단어 정보'}

    id = Column(String, name="ID", primary_key=True, default=lambda: str(uuid.uuid4()), comment="아이디")
    word = Column(String, name="WORD", comment="단어")
    word_abbr = Column(String, name="WORD_ABBR", comment="단어 약어")
    word_eng = Column(String, name="WORD_ENG", comment="단어 영문")
    word_desc = Column(String, name="WORD_DESC", comment="단어 설명")
    reg_dt = Column("REG_DT", DateTime, default=datetime.utcnow, comment="등록일시")
    mdfcn_dt = Column("MDFCN_DT", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="수정일시")


'''
용어마스터
'''
class FnWording(Base):
    __tablename__ = "TL_WORDING"
    __table_args__ = {'comment': '용어 정보'}

    id = Column(String, name="ID", primary_key=True, default=lambda: str(uuid.uuid4()), comment="아이디")
    wording_abbr = Column(String, name="WORDING_ABBR", comment="용어 약어")
    wording = Column(String, name="WORDING", comment="용어")
    wording_desc = Column(String, name="WORDING_DESC", comment="용어 설명")
    reg_dt = Column("REG_DT", DateTime, default=datetime.utcnow, comment="등록일시")
    mdfcn_dt = Column("MDFCN_DT", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="수정일시")

    # fn_mstr_id = Column("FN_MSTR", String, ForeignKey('TL_FN_MSTR.ID'))
    # fn_mstr = relationship("FnMaster", back_populates="fnInfos")
