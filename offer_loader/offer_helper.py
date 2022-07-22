


class OfferHelper():

    def find_nth_occurrence(self, string, char, occurrence):

        val = -1
        for i in range(0, occurrence):
            val = string.find(char, val + 1)
        return val