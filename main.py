import sqlite3
import json
import flask

app = flask.Flask(__name__)


def get_value_from_db(sql):
    with sqlite3.connect("netflix.db") as connect:
        connect.row_factory = sqlite3.Row
        result = connect.execute(sql).fetchall()

    return result


def search_by_title(title):
    for i in get_value_from_db(sql=f"""
    SELECT * 
    FROM netflix n
    WHERE title = '{title}'
    AND release_year = 
    (SELECT max(release_year) as max_value
    FROM netflix n
    WHERE title = '{title}')
    """):
        return dict(i)


@app.get('/movie/<title>/')
def search_title_view(title):
    response = search_by_title(title=title)
    a = {}
    for key in response.keys():
        if key in ["title", "country", "release_year"]:
            a[key] = response[key]

    return app.response_class(response=json.dumps(a),
                              status=200,
                              mimetype='application/json')


@app.get('/movie/<year1>/to/<year2>/')
def search_data_view(year1, year2):
    response = get_value_from_db(sql=f"""
    SELECT title, release_year 
    from netflix
    where release_year BETWEEN '{year1}' and '{year2}'
    LIMIT 100
    """)
    a = []
    for i in response:
        a.append(dict(i))

    return app.response_class(response=json.dumps(a),
                              status=200,
                              mimetype='application/json')


@app.get('/genre/<genre>/')
def search_rating_view(genre):
    response = get_value_from_db(sql=f"""
                SELECT *
                FROM netflix
                where listed_in LIKE '%{genre.title()}%'
                ORDER by release_year
                LIMIT 10""")

    a = []
    for i in response:
        a.append(dict(i))

    return app.response_class(response=json.dumps(a),
                              status=200,
                              mimetype='application/json')


@app.get('/rating/<rating>/')
def search_genre_view(rating):
    rating_dict = {
        "children":["G"],
        "family":["G", "PG", "PG-13"],
        "adult":["R", "NC-17"]
    }
    if rating in rating_dict:
        response = get_value_from_db(sql=f"""
               SELECT *
               from netflix
               where rating in {set(rating_dict[rating])}
               """)
    else:
        response = {'description':"Такой категории нет"}

    a = []
    for i in response:
        a.append(dict(i))

    return app.response_class(response=json.dumps(a),
                              status=200,
                              mimetype='application/json')


def step_5(name1, name2):
    response = get_value_from_db(
        f"""
            SELECT *
            from netflix
            where "cast" LIKE '%{name1}%' and "cast" LIKE '%{name2}%'
"""
    )

    names = []
    result = []

    for i in response:
        c = dict(i).get('case').split(", ")
        for k in c:
            names.append(k)

    b = [name1, name2]
    names = set(names)-set(b)

    for name in names:
        k = 0
        for i in response:
            if name in dict(i).get('case'):
                k+=1

        if k>2:
            result.append(name)

    return result


def step_6(type_film, year, genre):
    response = get_value_from_db(sql=f"""
    SELECT *
    FROM netflix
    WHERE "type" = '{type_film}'
    AND release_year = "{year}"
    AND listed_in LIKE '%{genre}%'
    """)

    a = []
    for i in response:
        a.append(dict(i))
    return json.dumps(a, indent=4)


app.run()
