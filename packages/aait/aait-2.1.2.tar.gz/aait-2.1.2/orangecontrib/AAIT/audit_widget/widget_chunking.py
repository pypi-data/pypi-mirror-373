import os
import sys
from Orange.data import Table, Domain, StringVariable
from AnyQt.QtWidgets import QApplication
from AnyQt.QtCore import QEventLoop

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\","/"):
     from Orange.widgets.orangecontrib.AAIT.widgets.OWChunking import OWChunker
     from Orange.widgets.orangecontrib.AAIT.audit_widget.SignalReceiver import SignalReceiver
else:
     from orangecontrib.AAIT.audit_widget.SignalReceiver import SignalReceiver
     from orangecontrib.AAIT.widgets.OWChunking import OWChunker


def check_create_chunker(chunker, receiver):
     text_var = StringVariable("content")
     domain = Domain([], metas=[text_var])
     table = Table.from_list(domain, [["In cognitive psychology, chunking is a process by which small individual pieces of a set of information are bound together to create a meaningful whole later on in memory.[1] The chunks, by which the information is grouped, are meant to improve short-term retention of the material, thus bypassing the limited capacity of working memory and allowing the working memory to be more efficient.[2][3][4] A chunk is a collection of basic units that are strongly associated with one another, and have been grouped together and stored in a person's memory. These chunks can be retrieved easily due to their coherent grouping.[5] It is believed that individuals create higher-order cognitive representations of the items within the chunk. The items are more easily remembered as a group than as the individual items themselves. These chunks can be highly subjective because they rely on an individual's perceptions and past experiences, which are linked to the information set. The size of the chunks generally ranges from two to six items but often differs based on language and culture.[6] According to Johnson (1970), there are four main concepts associated with the memory process of chunking: chunk, memory code, decode and recode.[7] The chunk, as mentioned prior, is a sequence of to-be-remembered information that can be composed of adjacent terms. These items or information sets are to be stored in the same memory code. The process of recoding is where one learns the code for a chunk, and decoding is when the code is translated into the information that it represents. The phenomenon of chunking as a memory mechanism is easily observed in the way individuals group numbers, and information, in day-to-day life. For example, when recalling a number such as 12101946, if numbers are grouped as 12, 10, and 1946, a mnemonic is created for this number as a month, day, and year. It would be stored as December 10, 1946, instead of a string of numbers. Similarly, another illustration of the limited capacity of working memory as suggested by George Miller can be seen from the following example: While recalling a mobile phone number such as 9849523450, we might break this into 98 495 234 50. Thus, instead of remembering 10 separate digits that are beyond the putative seven plus-or-minus two memory span, we are remembering four groups of numbers.[8] An entire chunk can also be remembered simply by storing the beginnings of a chunk in the working memory, resulting in the long-term memory recovering the remainder of the chunk.[4] Modality effect A modality effect is present in chunking. That is, the mechanism used to convey the list of items to the individual affects how much chunking occurs. Experimentally, it has been found that auditory presentation results in a larger amount of grouping in the responses of individuals than visual presentation does. Previous literature, such as George Miller's The Magical Number Seven, Plus or Minus Two: Some Limits on our Capacity for Processing Information (1956) has shown that the probability of recall of information is greater when the chunking strategy is used.[8] As stated above, the grouping of the responses occurs as individuals place them into categories according to their inter-relatedness based on semantic and perceptual properties. Lindley (1966) showed that since the groups produced have meaning to the participant, this strategy makes it easier for an individual to recall and maintain information in memory during studies and testing.[9] Therefore, when chunking is used as a strategy, one can expect a higher proportion of correct recalls.Memory training systems, mnemonicVarious kinds of memory training systems and mnemonics include training and drills in specially-designed recoding or chunking schemes.[10] Such systems existed before Miller's paper, but there was no convenient term to describe the general strategy and no substantive and reliable research. The term chunking is now often used in reference to these systems. As an illustration, patients with Alzheimer's disease typically experience working memory deficits; chunking is an effective method to improve patients' verbal working memory performance.[11] Patients with schizophrenia also experience working memory deficits which influence executive function; memory training procedures positively influence cognitive and rehabilitative outcomes.[12] Chunking has been proven to decrease the load on the working memory in many ways. As well as remembering chunked information easier, a person can also recall other non-chunked memories easier due to the benefits chunking has on the working memory.[4] For instance, in one study, participants with more specialized knowledge could reconstruct sequences of chess moves because they had larger chunks of procedural knowledge, which means that the level of expertise and the sorting order of the information retrieved is essential in the influence of procedural knowledge chunks retained in short-term memory.[13] Chunking has been shown to have an influence in linguistics, such as boundary perception.[14]Efficient Chunk sizesAccording to the research conducted by Dir lam (1972), a mathematical analysis was conducted to see what the efficient chunk size is. We are familiar with the size range that chunking holds, but Dir lam (1972) wanted to discover the most efficient chunk size. The mathematical findings have discovered that four or three items in each chunk is the most optimal.[15]"]])
     chunker.set_data(table)

     # Création d'une boucle d'attente pour simuler un chargement bloquant
     loop = QEventLoop( )
     # Connecte la fin du chargement pour quitter la boucle
     def on_finish():
         loop.quit()
     chunker.thread.finish.connect(on_finish)
     loop.exec_()
     chunker.Outputs.data.send = receiver.receive_data
     chunker.Outputs.data.send(chunker.result)
     data = receiver.received_data
     for line in data:
         print(line["Chunks"].value)
     if len(data[0]["Chunks"].value) > 0 :
             return 0
     else:
        return 1

def check_widget_chunker():
     app = QApplication(sys.argv)
     receiver = SignalReceiver()
     chunker = OWChunker()
     if check_create_chunker(chunker, receiver) != 0:
           print("Erreur à la création des embeddings")
           return 1
     return 0


if __name__ == "__main__":
     check_widget_chunker()