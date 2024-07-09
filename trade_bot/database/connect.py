from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import config


async_engine = create_async_engine(config.SQLALCHEMY_URL, 
                                   #echo=True
                                   )
async_session = async_sessionmaker(async_engine, expire_on_commit=False)

Base = declarative_base()

async def init_models():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def dispose_engine():
    await async_engine.dispose()