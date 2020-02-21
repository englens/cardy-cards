using System;
using System.Drawing;
using System.Windows.Forms;
using System.Windows.Input;
using System.IO;
using System.Text;
using System.Data.SQLite;
using System.Configuration;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
namespace CCD
{
    public partial class CCD : Form
    {
        SQLiteConnection cardDB;
        private string baseArt = @"/----------------------------------\
|                                  |
|                                  |
|                                  |
|                                  |
|                                  |
|                                  |
|                                  |
|                                  |
|                                  |
|                                  |
|                                  |
\----------------------------------/";
        public string BasePath = "../../../../"; //Path up to root cardy cards dir
        public string lastArt;
        private bool isArtChangedSelfTriggered;
        private bool artCleared;
        public CCD()
        {
            InitializeComponent();
            try
            {
                using (StreamReader file = File.OpenText(BasePath+"config.json"))
                using (JsonTextReader reader = new JsonTextReader(file))
                {
                    dynamic data = (JObject)JToken.ReadFrom(reader);
                    DBTextBox.Text = data.CCD.defaultDBPath;
                    ScriptLocTextBox.Text = data.CCD.defaultCardsPath;
                }
            }
            catch (FileNotFoundException)
            {
                //Generic values, see design screen
            }
            isArtChangedSelfTriggered = false;
            artCleared = false;
            lastArt = baseArt;
            artBox.Text = baseArt;
        }

        //this program simply just finds the DB and connects to it
        void connectToDB()
        {
            cardDB = new SQLiteConnection("Data Source=" + BasePath + DBTextBox.Text + ";Version=3");
            cardDB.Open();
        }

        bool IsCardAlreadyInDatabase(string cardTypeName, string className)
        {
            string query = @"SELECT EXISTS(
                                    SELECT 1 FROM CardType
                                    WHERE CardType.name=@name
                                    OR CardType.class_name=@cname
                             );";
            SQLiteCommand command = new SQLiteCommand(query, cardDB);
            command.Parameters.AddWithValue("@name", cardTypeName);
            command.Parameters.AddWithValue("@cname", className);
            return command.ExecuteScalar().ToString().Equals("0");            
        }

        //ths function will take the data in the datagrid rows and put them in the query string to add to the DB
        void fillParamType()
        {
            //first, we need to collect the card id
            string query = "SELECT last_insert_rowid();";

            //next, we create a command to go and extract said card id
            SQLiteCommand retrieveID = new SQLiteCommand(query, cardDB);

            //we create a variable to house that informaton
            var data = retrieveID.ExecuteScalar();

            //loop through each row in each column
            foreach (DataGridViewRow row in paramTable.Rows)
            {

                if (row.Cells[0].Value != null)
                {
                    //add to the query the data from the cells and the card id from before
                    query += "insert into ParamType (name, value_default, max_default, visible_default, card_type_id) values (\"" +
                    row.Cells[0].Value + "\",\"" +
                    row.Cells[1].Value + "\",\"" +
                    row.Cells[2].Value + "\",\"" +
                    row.Cells[3].Value + "\",\"" +
                    data.ToString() + "\");";
                }
            }

            //make final command from it
            SQLiteCommand sendIT = new SQLiteCommand(query, cardDB);

            //execute order 66
            sendIT.ExecuteNonQuery();
        }

        //this function will take text from the textboxes and form the query with them to send to the DB
        void fillCardType()
        {
            //we create the string that will hold the wuery with its values to submit
            string query = "insert into CardType (name, rarity, description, art, class_name) values (\"" +
            nameInput.Text +
            "\",\"" + rarityInput.Text +
            "\",\"" + descriptionInput.Text +
            "\",\"" + artBox.Text +
            "\",\"" + classInput.Text + "\");";

            //we create the command to execute
            SQLiteCommand sendIT = new SQLiteCommand(query, cardDB);

            //we execute the command
            sendIT.ExecuteNonQuery();
        }

        //this function will create a py script for every card created
        void createPyClass()
        {

            //we create the path and name of file for this card
            string pyScript = BasePath + ScriptLocTextBox.Text + "/" + classInput.Text + ".py";

            //we check if this file already exists
            if (File.Exists(pyScript))
            {
                //if it does, we rename the new file semi-iteratively
                pyScript = ScriptLocTextBox.Text + classInput.Text + "_1.py";
            }

            //we create the text to file the script with
            //the uncomfortable text formatting is left this way on purpose, so that it looks programmatically clean in the py script
            string pyText = @"from game_objects import card

class " + classInput.Text + @"(card.Card):
    def use(self, message) -> str:
        raise NotImplementedError
    
    def passive(self, message, t, last_t) -> str:
        raise NotImplementedError
";

            //we create the file in this function
            using (FileStream fs = File.Create(pyScript))
            {
                //we store the text into a byte array and write to the file
                Byte[] info = new UTF8Encoding(true).GetBytes(pyText);
                fs.Write(info, 0, info.Length);
            }

        }
        private bool DataValid()
        {
            if(classInput.Text.Length == 0 ||
               rarityInput.Text.Length == 0 ||
               nameInput.Text.Length == 0)
            {
                return false;
            }
            return true;
        }
        //we call the functions here when submit is presed
        private void SubmitButton_Click(object sender, EventArgs e)
        {
            connectToDB();
            
            //we wanna make sure the card submitted has the correct format before submitting
            if (artBox.Text.Length != baseArt.Length)
            {
                MessageBox.Show("Card Art incorrect Legnth");
                return;
            }

            //Make sure the user actually entered data
            if (!DataValid())
            {
                MessageBox.Show("Error: Improper Data field(s)");
                return;
            }

            if (!IsCardAlreadyInDatabase(nameInput.Text, classInput.Text))
            {
                MessageBox.Show("Card with that name or class name already in database.");
                return;
            }

            fillCardType();
            fillParamType();
            createPyClass();

            //let the user know their card has been submit
            MessageBox.Show("Card sucessfully submitted!");
        }

        //this will delete selected rows by the user
        private void DeleteButton_Click(object sender, EventArgs e)
        {
            Int32 selectedRowCount = paramTable.Rows.GetRowCount(DataGridViewElementStates.Selected);
            if (selectedRowCount > 0)
            {
                for (int i = 0; i < selectedRowCount; i++)
                {
                    paramTable.Rows.RemoveAt(paramTable.SelectedRows[0].Index);
                }
            }
        }

        //This is for finding the location for saving the py scripts
        private void FindScriptsTextBox_Click(object sender, EventArgs e)
        {
            FolderBrowserDialog findDirectory = new FolderBrowserDialog();

            if (findDirectory.ShowDialog() == System.Windows.Forms.DialogResult.OK)
            {
                ScriptLocTextBox.Text = findDirectory.SelectedPath;
            }
        }

        //This is for finding the database file you want to use
        private void DBTextBox_Click(object sender, EventArgs e)
        {
            OpenFileDialog openDB = new OpenFileDialog();

            openDB.Filter = "DB Files|*.db";
            if (openDB.ShowDialog() == System.Windows.Forms.DialogResult.OK)
            {
                DBTextBox.Text = openDB.SafeFileName;
            }
        }

        //This button resets the card art box to its default format
        private void ClearArtBtn_Click(object sender, EventArgs e)
        {
            artCleared = true;
            artBox.Text = baseArt;
            lastArt = baseArt;
            artCleared = false;
        }

        private void artBox_TextChanged(object sender, EventArgs e)
        {
            if (isArtChangedSelfTriggered)
            {
                isArtChangedSelfTriggered = false;
                return;
            }
            var oldSS = artBox.SelectionStart;
            if (artBox.Text.Length == lastArt.Length + 1) // Character increased
            {
                isArtChangedSelfTriggered = true;
                artBox.Text = artBox.Text.Remove(artBox.SelectionStart, 1);
                lastArt = artBox.Text;
            }
            else if (artBox.Text.Length == lastArt.Length - 1) // Erase 1
            {
                isArtChangedSelfTriggered = true;
                artBox.Text = artBox.Text.Insert(artBox.SelectionStart, " ");
                lastArt = artBox.Text;
            }
            else
            {
                if (!artCleared)
                {
                    artBox.Text = lastArt;
                }
                
            }
            artBox.SelectionStart = oldSS;

        }
    }
}