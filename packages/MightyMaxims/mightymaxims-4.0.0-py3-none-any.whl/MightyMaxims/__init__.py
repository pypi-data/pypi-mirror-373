'''
Mighty Maxims: Short & Memorable Quotations.
Project: https://github.com/soft9000/DoctorQuote
Paperback: https://www.amazon.com/dp/B09H9DV8KV
Group: https://www.facebook.com/groups/mightymaxims

>>> import MightyMaxims
>>> MightyMaxims.GetQuote()
'''

__all__ = ['GetQuote']


def GetQuote():
    ''' Display a random quotation. '''
    import MightyMaxims.GetRandom as app
    app.get_random()

GetQuote()

