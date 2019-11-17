model_css = '''
    .card {
        font-family: arial;
        font-size: 20px;
        text-align: center;
        color: black;
        background-color:
        white;
        }
    .from {
        font-style: italic;
    }'''

std_word = """
    <h3 style="text-align: center;">{{Word}}</h3>
    <blockquote>
    <div style="text-align: center;">{{Grammar}}</div>
    <div style="text-align: center;">{{Pronunciation}}</div>
    </blockquote>
    <div style="text-align: center;">{{Meaning}}</div>
    <br>
    <div style="text-align: center; font-style: italic;">{{Examples}}</div>
    """

std_word_def = """
    <h3 style="text-align: center;">{{Word}}</h3>
    <blockquote>
    <div style="text-align: center;">{{Grammar}}</div>
    <div style="text-align: center;">{{Pronunciation}}</div>
    </blockquote>
    <div style="text-align: center;">{{Meaning}}</div>
    <br>
    <div style="text-align: center;">{{Definition}}</div>
    """

std_def = """
    <div style="text-align: center;">{{Definition}}</div>
    """

std_def_sound = """
    <div style="text-align: center;">{{Definition}}</div>
    <div style="text-align: center;">{{Audio}}</div>
    """

std_word_sound = """
    <h3 style="text-align: center;">{{Word}}</h3>
    <blockquote>
    <div style="text-align: center;">{{Grammar}}</div>
    <div style="text-align: center;">{{Pronunciation}}</div>
    </blockquote>
    <div style="text-align: center;">{{Meaning}}</div>
    <br>
    <div style="text-align: center;font-style: italic;">{{Examples}}</div>
    <br>
    <div style="text-align: center;">{{Audio}}</div>
    """

std_sound = """
    <div style="text-align: center;">Listen.{{Audio}}</div>
    """
    