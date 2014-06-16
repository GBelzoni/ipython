import pandas as pd
from IPython.display import display
import pickle

class DataLabeler(object):
    
    def __init__(self, data, q_and_a, description="No description", label_loc="./labels.pkl",display_cols = None):  

        #Input Variables
        self.data = data
        self.q_and_a = q_and_a
        self.display_cols = display_cols
        self.label_loc = label_loc
        self.description = description

        
        #Initialise internal state
        self.df_labeled = pd.DataFrame(columns=['index','label','description'])
        self.label_counter = 0 #Counts examples labelled
        data_tolabel = self.data.iloc[self.label_counter]
        self.data_tolabel = pd.DataFrame(data_tolabel).transpose()


        #Initial display
        display(data_tolabel)
        
    
    def input_handler(self,**kwargs):

        ######Handle Event input
        input_dict = kwargs['LabellerWidget']
        try:
            inpt = input_dict['key_num'] #Will fail with no input, ie on first loop

        except:
            inpt = "no input"

        self.label_handler(inpt)
        self.save_handler(inpt)
        self.load_saved_handler(inpt)
        self.reverse_tag(inpt)
        self.display() 

    def load_saved_handler(self,inpt):

        if inpt == str(76):
            with open(self.label_loc) as fin:
                self.df_labeled = pickle.load(fin)


            self.label_counter = self.df_labeled.shape[0]+1
            #Updata current data to next data to be labelled
            data_tolabel = self.data.iloc[self.label_counter]
            self.data_tolabel = pd.DataFrame(data_tolabel).transpose()

    def reverse_tag(self,inpt):

        if inpt == str(82):
            if self.label_counter ==0:
                return
            self.label_counter -= 1
            data_tolabel = self.data.iloc[self.label_counter]
            self.data_tolabel = pd.DataFrame(data_tolabel).transpose()
            
            self.df_labeled = self.df_labeled.iloc[1:]


    def save_handler(self,inpt):

        if inpt == str(83) and self.df_labeled.shape[0] !=0: #if input = 's' and labels in data frame
            with open(self.label_loc, 'w') as fout:
                pickle.dump(self.df_labeled,fout)
                fout.close()

    def label_handler(self,inpt):

        #Check if input is in answers
        in_answers = False
        
        for ans in self.q_and_a['answers']:

            if inpt == ans['key_num']:
                this_label = ans['label']
                in_answers = True
                break
            else:
                this_label = None

        if in_answers:
            #Add this label to labelled
            #Make dataframe of current label
            this_labelled = pd.DataFrame( [self.data_tolabel.index[0], this_label, self.description]).transpose()
            this_labelled.columns = ['index','label','description']
            #Concatenate to labelled
            self.df_labeled = pd.concat([ this_labelled, self.df_labeled])
            #increase label counter
            self.label_counter += 1
            #Updata current data to next data to be labelled
            data_tolabel = self.data.iloc[self.label_counter]
            self.data_tolabel = pd.DataFrame(data_tolabel).transpose()

  
    def display(self):
        #####Display Info
        
        print('Description of tagging session: {}'.format(self.description) )
        #Display question
        print('Question: ' +  self.q_and_a['question'])
        #Display answer options
        print("Answers")
        answers_text = [ans['answer_text'] for ans in self.q_and_a['answers']]
        print(" | ".join(answers_text))
        print("Save data press 's', Load data press 'l', Reverse Answer 'r'")
        print("So far have labelled {} examples".format(self.label_counter))
        #Display Data
        if self.display_cols == None: 
            display(self.data_tolabel)
        else:
            display(self.data_tolabel[self.display_cols].reset_index(drop=True,inplace=False))

        #Display data merged labelled
        print("Labelled Data")

        #Display labeled text
        df_output_display = pd.merge(self.data, self.df_labeled,left_index=True, right_on='index')
           
        if df_output_display.shape[0]!= 0:
            if self.display_cols != None: 
                output_display_cols = self.display_cols + ['label']
                df_output_display = df_output_display[output_display_cols]
            display(df_output_display.sort_index(ascending=False))
        
        

