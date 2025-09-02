#    FreeStylo
#    A tool for the analysis of literary texts.
#    Copyright (C) 2024  Felix Schneider
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import freestylo.TextObject as to
import freestylo.MetaphorAnnotation as ma
import freestylo.TextPreprocessor as tp
import numpy as np
import os


def test_metaphor_annotation():
    """
    Test the MetaphorAnnotation class.
    """
    text = to.TextObject(
            text = "Das ist ein wilder Satz mit zwei waghalsigen Metaphern. Nicht so wie warmes Wasser oder kaltes Eis.""",
            language="de")
    preprocessor = tp.TextPreprocessor(language="de")
    preprocessor.process_text(text)


    metaphor = ma.MetaphorAnnotation(
            text=text)
    metaphor.find_candidates()
    metaphor.load_model(os.path.expanduser("~/.freestylo/models/metaphor_de.torch"))
    metaphor.score_candidates()
    results = metaphor.candidates

    scores = [c.score for c in metaphor.candidates]
    indices = np.argsort(scores)


    def is_result(candidate, string):
        wordstring = " ".join(text.tokens[candidate.ids[0]:candidate.ids[1]+1])
        return wordstring == string


    assert(len(results) == 4)
    for i in range(0, 2):
        assert(text.tokens[results[indices[i]].ids[0]] in ["warmes", "kaltes"])
    for i in range(2, 4):
        assert(text.tokens[results[indices[i]].ids[0]] in ["wilder", "waghalsigen"])


    print(text.tokens)
    for candidate in metaphor.candidates:
        print(" ".join(text.tokens[candidate.ids[0]:candidate.ids[1]+1]))
        print("ids", candidate.ids)
        print("score:", candidate.score)
        print("")




if __name__ == "__main__":
    test_metaphor_annotation()


