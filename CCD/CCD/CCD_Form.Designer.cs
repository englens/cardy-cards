namespace CCD
{
    partial class CCD
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(CCD));
            this.nameLabel = new System.Windows.Forms.Label();
            this.nameInput = new System.Windows.Forms.TextBox();
            this.rarityLabel = new System.Windows.Forms.Label();
            this.rarityInput = new System.Windows.Forms.TextBox();
            this.descriptionLabel = new System.Windows.Forms.Label();
            this.descriptionInput = new System.Windows.Forms.TextBox();
            this.artBox = new System.Windows.Forms.TextBox();
            this.paramTable = new System.Windows.Forms.DataGridView();
            this.paramLabel = new System.Windows.Forms.Label();
            this.submitButton = new System.Windows.Forms.Button();
            this.classLabel = new System.Windows.Forms.Label();
            this.classInput = new System.Windows.Forms.TextBox();
            this.deleteButton = new System.Windows.Forms.Button();
            this.scriptsLabel = new System.Windows.Forms.Label();
            this.dbLabel = new System.Windows.Forms.Label();
            this.clearArtBtn = new System.Windows.Forms.Button();
            this.DBTextBox = new System.Windows.Forms.TextBox();
            this.ScriptLocTextBox = new System.Windows.Forms.TextBox();
            this.textBox1 = new System.Windows.Forms.TextBox();
            this.label1 = new System.Windows.Forms.Label();
            this.nameCol = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.valueDCOL = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.maxDCOL = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.visibleDCOL = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.LocToolTip = new System.Windows.Forms.ToolTip(this.components);
            ((System.ComponentModel.ISupportInitialize)(this.paramTable)).BeginInit();
            this.SuspendLayout();
            // 
            // nameLabel
            // 
            this.nameLabel.Anchor = System.Windows.Forms.AnchorStyles.None;
            this.nameLabel.AutoSize = true;
            this.nameLabel.Location = new System.Drawing.Point(37, 15);
            this.nameLabel.Name = "nameLabel";
            this.nameLabel.Size = new System.Drawing.Size(38, 13);
            this.nameLabel.TabIndex = 1;
            this.nameLabel.Text = "Name:";
            // 
            // nameInput
            // 
            this.nameInput.Anchor = System.Windows.Forms.AnchorStyles.None;
            this.nameInput.Font = new System.Drawing.Font("Microsoft Sans Serif", 11F);
            this.nameInput.Location = new System.Drawing.Point(81, 8);
            this.nameInput.Name = "nameInput";
            this.nameInput.Size = new System.Drawing.Size(234, 24);
            this.nameInput.TabIndex = 1;
            // 
            // rarityLabel
            // 
            this.rarityLabel.Anchor = System.Windows.Forms.AnchorStyles.None;
            this.rarityLabel.AutoSize = true;
            this.rarityLabel.Location = new System.Drawing.Point(38, 46);
            this.rarityLabel.Name = "rarityLabel";
            this.rarityLabel.Size = new System.Drawing.Size(37, 13);
            this.rarityLabel.TabIndex = 3;
            this.rarityLabel.Text = "Rarity:";
            // 
            // rarityInput
            // 
            this.rarityInput.Anchor = System.Windows.Forms.AnchorStyles.None;
            this.rarityInput.Font = new System.Drawing.Font("Microsoft Sans Serif", 11F);
            this.rarityInput.Location = new System.Drawing.Point(81, 39);
            this.rarityInput.Name = "rarityInput";
            this.rarityInput.Size = new System.Drawing.Size(234, 24);
            this.rarityInput.TabIndex = 2;
            // 
            // descriptionLabel
            // 
            this.descriptionLabel.Anchor = System.Windows.Forms.AnchorStyles.None;
            this.descriptionLabel.AutoSize = true;
            this.descriptionLabel.Location = new System.Drawing.Point(15, 192);
            this.descriptionLabel.Name = "descriptionLabel";
            this.descriptionLabel.Size = new System.Drawing.Size(63, 13);
            this.descriptionLabel.TabIndex = 6;
            this.descriptionLabel.Text = "Description:";
            // 
            // descriptionInput
            // 
            this.descriptionInput.Anchor = System.Windows.Forms.AnchorStyles.None;
            this.descriptionInput.Location = new System.Drawing.Point(81, 100);
            this.descriptionInput.Multiline = true;
            this.descriptionInput.Name = "descriptionInput";
            this.descriptionInput.Size = new System.Drawing.Size(234, 197);
            this.descriptionInput.TabIndex = 4;
            // 
            // artBox
            // 
            this.artBox.AllowDrop = true;
            this.artBox.Anchor = System.Windows.Forms.AnchorStyles.None;
            this.artBox.Font = new System.Drawing.Font("Courier New", 11F);
            this.artBox.Location = new System.Drawing.Point(321, 69);
            this.artBox.MaximumSize = new System.Drawing.Size(334, 228);
            this.artBox.MaxLength = 500;
            this.artBox.MinimumSize = new System.Drawing.Size(334, 228);
            this.artBox.Multiline = true;
            this.artBox.Name = "artBox";
            this.artBox.Size = new System.Drawing.Size(334, 228);
            this.artBox.TabIndex = 5;
            this.artBox.TextChanged += new System.EventHandler(this.artBox_TextChanged);
            // 
            // paramTable
            // 
            this.paramTable.AllowUserToResizeColumns = false;
            this.paramTable.AllowUserToResizeRows = false;
            this.paramTable.Anchor = System.Windows.Forms.AnchorStyles.None;
            this.paramTable.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.paramTable.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.nameCol,
            this.valueDCOL,
            this.maxDCOL,
            this.visibleDCOL});
            this.paramTable.Location = new System.Drawing.Point(81, 308);
            this.paramTable.Name = "paramTable";
            this.paramTable.RowHeadersWidth = 82;
            this.paramTable.Size = new System.Drawing.Size(453, 147);
            this.paramTable.TabIndex = 10;
            // 
            // paramLabel
            // 
            this.paramLabel.Anchor = System.Windows.Forms.AnchorStyles.None;
            this.paramLabel.AutoSize = true;
            this.paramLabel.Location = new System.Drawing.Point(15, 379);
            this.paramLabel.Name = "paramLabel";
            this.paramLabel.Size = new System.Drawing.Size(63, 26);
            this.paramLabel.TabIndex = 11;
            this.paramLabel.Text = "Card\r\nParameters:";
            // 
            // submitButton
            // 
            this.submitButton.Anchor = System.Windows.Forms.AnchorStyles.None;
            this.submitButton.Location = new System.Drawing.Point(879, 461);
            this.submitButton.Name = "submitButton";
            this.submitButton.Size = new System.Drawing.Size(136, 41);
            this.submitButton.TabIndex = 12;
            this.submitButton.Text = "Submit Card";
            this.submitButton.UseVisualStyleBackColor = true;
            this.submitButton.Click += new System.EventHandler(this.SubmitButton_Click);
            // 
            // classLabel
            // 
            this.classLabel.Anchor = System.Windows.Forms.AnchorStyles.None;
            this.classLabel.AutoSize = true;
            this.classLabel.Location = new System.Drawing.Point(9, 77);
            this.classLabel.Name = "classLabel";
            this.classLabel.Size = new System.Drawing.Size(66, 13);
            this.classLabel.TabIndex = 13;
            this.classLabel.Text = "Class Name:";
            // 
            // classInput
            // 
            this.classInput.Anchor = System.Windows.Forms.AnchorStyles.None;
            this.classInput.Font = new System.Drawing.Font("Microsoft Sans Serif", 11F);
            this.classInput.Location = new System.Drawing.Point(81, 70);
            this.classInput.Name = "classInput";
            this.classInput.Size = new System.Drawing.Size(234, 24);
            this.classInput.TabIndex = 3;
            // 
            // deleteButton
            // 
            this.deleteButton.Anchor = System.Windows.Forms.AnchorStyles.None;
            this.deleteButton.Location = new System.Drawing.Point(540, 410);
            this.deleteButton.Name = "deleteButton";
            this.deleteButton.Size = new System.Drawing.Size(115, 45);
            this.deleteButton.TabIndex = 15;
            this.deleteButton.Text = "Delete Row";
            this.deleteButton.UseVisualStyleBackColor = true;
            this.deleteButton.Click += new System.EventHandler(this.DeleteButton_Click);
            // 
            // scriptsLabel
            // 
            this.scriptsLabel.Anchor = System.Windows.Forms.AnchorStyles.None;
            this.scriptsLabel.AutoSize = true;
            this.scriptsLabel.Location = new System.Drawing.Point(329, 46);
            this.scriptsLabel.Name = "scriptsLabel";
            this.scriptsLabel.Size = new System.Drawing.Size(86, 13);
            this.scriptsLabel.TabIndex = 16;
            this.scriptsLabel.Text = "Scripts Location:";
            this.LocToolTip.SetToolTip(this.scriptsLabel, "Modify in config.json");
            // 
            // dbLabel
            // 
            this.dbLabel.Anchor = System.Windows.Forms.AnchorStyles.None;
            this.dbLabel.AutoSize = true;
            this.dbLabel.Location = new System.Drawing.Point(346, 13);
            this.dbLabel.Name = "dbLabel";
            this.dbLabel.Size = new System.Drawing.Size(69, 13);
            this.dbLabel.TabIndex = 19;
            this.dbLabel.Text = "DB Location:";
            this.LocToolTip.SetToolTip(this.dbLabel, "Modify in config.json");
            // 
            // clearArtBtn
            // 
            this.clearArtBtn.Anchor = System.Windows.Forms.AnchorStyles.None;
            this.clearArtBtn.Location = new System.Drawing.Point(540, 360);
            this.clearArtBtn.Name = "clearArtBtn";
            this.clearArtBtn.Size = new System.Drawing.Size(115, 44);
            this.clearArtBtn.TabIndex = 22;
            this.clearArtBtn.Text = "Clear Art";
            this.clearArtBtn.UseVisualStyleBackColor = true;
            this.clearArtBtn.Click += new System.EventHandler(this.ClearArtBtn_Click);
            // 
            // DBTextBox
            // 
            this.DBTextBox.Anchor = System.Windows.Forms.AnchorStyles.None;
            this.DBTextBox.Font = new System.Drawing.Font("Microsoft Sans Serif", 11F);
            this.DBTextBox.Location = new System.Drawing.Point(421, 8);
            this.DBTextBox.Name = "DBTextBox";
            this.DBTextBox.ReadOnly = true;
            this.DBTextBox.Size = new System.Drawing.Size(234, 24);
            this.DBTextBox.TabIndex = 23;
            this.DBTextBox.Text = "confg.json not loaded";
            this.LocToolTip.SetToolTip(this.DBTextBox, "Modify in config.json");
            // 
            // ScriptLocTextBox
            // 
            this.ScriptLocTextBox.Anchor = System.Windows.Forms.AnchorStyles.None;
            this.ScriptLocTextBox.Font = new System.Drawing.Font("Microsoft Sans Serif", 11F);
            this.ScriptLocTextBox.Location = new System.Drawing.Point(421, 39);
            this.ScriptLocTextBox.Name = "ScriptLocTextBox";
            this.ScriptLocTextBox.ReadOnly = true;
            this.ScriptLocTextBox.Size = new System.Drawing.Size(234, 24);
            this.ScriptLocTextBox.TabIndex = 24;
            this.ScriptLocTextBox.Text = "confg.json not loaded";
            this.LocToolTip.SetToolTip(this.ScriptLocTextBox, "Modify in config.json");
            // 
            // textBox1
            // 
            this.textBox1.Anchor = System.Windows.Forms.AnchorStyles.None;
            this.textBox1.Font = new System.Drawing.Font("Courier New", 11F);
            this.textBox1.Location = new System.Drawing.Point(661, 8);
            this.textBox1.Multiline = true;
            this.textBox1.Name = "textBox1";
            this.textBox1.ReadOnly = true;
            this.textBox1.Size = new System.Drawing.Size(354, 447);
            this.textBox1.TabIndex = 25;
            this.textBox1.Text = resources.GetString("textBox1.Text");
            // 
            // label1
            // 
            this.label1.Anchor = System.Windows.Forms.AnchorStyles.None;
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(601, 300);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(54, 13);
            this.label1.TabIndex = 26;
            this.label1.Text = "^ Card Art";
            // 
            // nameCol
            // 
            this.nameCol.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.ColumnHeader;
            this.nameCol.HeaderText = "name";
            this.nameCol.MinimumWidth = 10;
            this.nameCol.Name = "nameCol";
            this.nameCol.Resizable = System.Windows.Forms.DataGridViewTriState.True;
            this.nameCol.Width = 58;
            // 
            // valueDCOL
            // 
            this.valueDCOL.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.ColumnHeader;
            this.valueDCOL.HeaderText = "value_default";
            this.valueDCOL.MinimumWidth = 10;
            this.valueDCOL.Name = "valueDCOL";
            this.valueDCOL.Resizable = System.Windows.Forms.DataGridViewTriState.True;
            this.valueDCOL.Width = 96;
            // 
            // maxDCOL
            // 
            this.maxDCOL.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.ColumnHeader;
            this.maxDCOL.HeaderText = "max_default";
            this.maxDCOL.MinimumWidth = 10;
            this.maxDCOL.Name = "maxDCOL";
            this.maxDCOL.Resizable = System.Windows.Forms.DataGridViewTriState.True;
            this.maxDCOL.Width = 89;
            // 
            // visibleDCOL
            // 
            this.visibleDCOL.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.ColumnHeader;
            this.visibleDCOL.HeaderText = "visible_default";
            this.visibleDCOL.MinimumWidth = 10;
            this.visibleDCOL.Name = "visibleDCOL";
            this.visibleDCOL.Resizable = System.Windows.Forms.DataGridViewTriState.True;
            this.visibleDCOL.Width = 99;
            // 
            // CCD
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.AutoScroll = true;
            this.ClientSize = new System.Drawing.Size(1024, 508);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.textBox1);
            this.Controls.Add(this.ScriptLocTextBox);
            this.Controls.Add(this.DBTextBox);
            this.Controls.Add(this.clearArtBtn);
            this.Controls.Add(this.dbLabel);
            this.Controls.Add(this.scriptsLabel);
            this.Controls.Add(this.deleteButton);
            this.Controls.Add(this.classInput);
            this.Controls.Add(this.classLabel);
            this.Controls.Add(this.submitButton);
            this.Controls.Add(this.paramLabel);
            this.Controls.Add(this.paramTable);
            this.Controls.Add(this.artBox);
            this.Controls.Add(this.descriptionInput);
            this.Controls.Add(this.descriptionLabel);
            this.Controls.Add(this.rarityInput);
            this.Controls.Add(this.rarityLabel);
            this.Controls.Add(this.nameInput);
            this.Controls.Add(this.nameLabel);
            this.MaximumSize = new System.Drawing.Size(1040, 547);
            this.MinimumSize = new System.Drawing.Size(1040, 547);
            this.Name = "CCD";
            this.Text = "Cardy Cards Designer";
            this.LocToolTip.SetToolTip(this, "Modify in config.json");
            ((System.ComponentModel.ISupportInitialize)(this.paramTable)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion
        private System.Windows.Forms.Label nameLabel;
        private System.Windows.Forms.TextBox nameInput;
        private System.Windows.Forms.Label rarityLabel;
        private System.Windows.Forms.TextBox rarityInput;
        private System.Windows.Forms.Label descriptionLabel;
        private System.Windows.Forms.TextBox descriptionInput;
        private System.Windows.Forms.TextBox artBox;
        private System.Windows.Forms.DataGridView paramTable;
        private System.Windows.Forms.Label paramLabel;
        private System.Windows.Forms.Button submitButton;
        private System.Windows.Forms.Label classLabel;
        private System.Windows.Forms.TextBox classInput;
        private System.Windows.Forms.Button deleteButton;
        private System.Windows.Forms.Label scriptsLabel;
        private System.Windows.Forms.Label dbLabel;
        private System.Windows.Forms.Button clearArtBtn;
        private System.Windows.Forms.TextBox DBTextBox;
        private System.Windows.Forms.TextBox ScriptLocTextBox;
        private System.Windows.Forms.TextBox textBox1;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.DataGridViewTextBoxColumn nameCol;
        private System.Windows.Forms.DataGridViewTextBoxColumn valueDCOL;
        private System.Windows.Forms.DataGridViewTextBoxColumn maxDCOL;
        private System.Windows.Forms.DataGridViewTextBoxColumn visibleDCOL;
        private System.Windows.Forms.ToolTip LocToolTip;
    }
}



