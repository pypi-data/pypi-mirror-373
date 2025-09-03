import matplotlib.pyplot as plt
import os

class markdownMaker:
    def __init__(self,ouputFolder,fileName) -> None:
        self.content = []
        self.ouputFolder = ouputFolder
        self.fileName = fileName
        self.figure_counter = 0
        os.system("mkdir "+self.ouputFolder)
        os.system("mkdir "+self.ouputFolder+"/figures")


    def add_picture(self, ouputFile=None):
        ouputFile = ouputFile if ouputFile else "figures/fig_" + str(self.figure_counter) +".png"
        self.figure_counter +=1
        plt.savefig(self.ouputFolder+'/'+ouputFile)
        self.content.append("![" +ouputFile +"](" +ouputFile +")")

    def save(self):
        with open(self.ouputFolder+"/"+self.fileName,"w") as f:
            for x in self.content:
                f.write(x+"\n")
           
    def add_text(self,txt):
        self.content.append(txt)

    def add_section(self,txt):
        self.content.append('\n' + txt +'\n')        
        
    def add_title(self, txt, level = 1):
        h = ""
        for i in range(level):
            h+="#"
        self.content.append(h +" " + txt +'\n')
        
        
    def add_table(self, df, caption = None, label = None):
        if caption:
            self.content.append("\n"+caption)
        if label:
            self.content.append("\n"+label)

        # convert df to markdown without the entry column 
        
        self.content.append(df.to_markdown(index = False))
        self.content.append("\n")
        