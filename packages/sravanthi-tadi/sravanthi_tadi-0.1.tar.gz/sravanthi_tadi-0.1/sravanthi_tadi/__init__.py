class SravanthiTadi:
    def __str__(self):
        return (
            "Hi, I'm Sravanthi.\n"
            "Present nenu B.Tech 2nd year, CSE chaduvuthunnanu...!.\n"
            "Naku ma amma, nannante chaala istam...!.\n"
            "Present aite machine learning, data science nerchukuntunnanu...!.\n"
            "inka na gurinchi cheppalante, aha, anni cheppestara enti...?...!.\n"
            "Tarvata Maatladukundam...!.\n"
            "ika unta mari bye bye...!.\n"
        )

    def __repr__(self):
        return self.__str__()

import sys
sys.modules[__name__] = SravanthiTadi()
