html = """<div class="tooltip">{text}<div class="tooltip-bottom">
        <div class="between">
            <a href="{link}" class="normal">
                {meaning}
            </a>
            <span class="normal">{level}</span>
        </div>
        <div class="component-list">
            <span>
                {component_list}
            </span>
            <div class="flex">
             <span class="blue">ON: {onyomi}</span> 
             <span>|</span>
             <span class="green">KUN: {kunyomi}</span>
            </div>
        </div>
        <div class="meaning-mnemonic">
            {meaning_mnemonic}
        </div>
        <div class="reading-mnemonic">
            {reading_mnemonic}
        </div>
    </div>
</div>"""

css = """
.tooltip {
    display:inline-block;
    position:relative;
    border-bottom:1px dotted #666;
    text-align:left;
    cursor: pointer;
}
.tooltip-bottom {
    width: max-content;
    min-width:100px;
    max-width:400px;
    left:50%;
    transform:translate(-50%, 0);
    padding:10px;
    color:#666666;
    background-color:#EEEEEE;
    font-family: "sans-serif";
    font-weight:normal;
    font-size:14px;
    border-radius:8px;
    position:absolute;
    z-index:99999999;
    box-sizing:border-box;
    box-shadow:0 1px 8px rgba(0,0,0,0.5);
    display:none;
}
.normal {
    font-size:16px;
    color: red;
    font-weight:bold;
}
.tooltip:hover .tooltip-bottom {
    display:block;
}
.meaning-mnemonic {
    border-top:2px solid #666;
    border-bottom:2px solid #666;
    padding: 5px 0px;
	margin: 5px 0px;
}
.tooltip-bottom radical, kanji, vocabulary, reading, ja {
    font-weight: bold;
}
.tooltip-bottom span {
    font-weight: bold;
    color: red;
}
.green {
color: green;
}
.blue {
color: blue;
}
.component-list {
display: grid;
gap: 2;
}
.flex {
display: flex;
gap: 2;
}
.between {
display: flex;
justify-content: space-between;
}
"""
