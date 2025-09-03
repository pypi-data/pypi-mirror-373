from pydantic import BaseModel


class Credits(BaseModel):
    credits: int | float

    @staticmethod
    def zero() -> 'Credits':
        return Credits(credits=0)
