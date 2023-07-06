PRAGMA foreign_keys = ON;

INSERT INTO users(username, fullname, email, filename, password) VALUES 
    ('awdeorio', 'Andrew DeOrio', 'awdeorio@umich.edu', 'e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg', 'sha512$a9845263667747cfa57a69c615e1d067$b7a02dfe13dc844a3d8137596e2cfbc050fc6546708dd70c59cb2a435292293930cb68a6d3d684b328d0bc7b63be77f1cc041863c237bf665b99d0419eff76ac'),
    ('jflinn', 'Jason Flinn', 'jflinn@umich.edu', '505083b8b56c97429a728b68f31b0b2a089e5113.jpg', 'password'),
    ('michjc', 'Michael Cafarella', 'michjc@umich.edu', '5ecde7677b83304132cb2871516ea50032ff7a4f.jpg', 'password'),
    ('jag', 'H.V. Jagadish', 'jag@umich.edu', '73ab33bd357c3fd42292487b825880958c595655.jpg', 'password');

INSERT INTO posts(filename, owner) VALUES
    ('122a7d27ca1d7420a1072f695d9290fad4501a41.jpg', 'awdeorio'),
    ('ad7790405c539894d25ab8dcf0b79eed3341e109.jpg', 'jflinn'),
    ('9887e06812ef434d291e4936417d125cd594b38a.jpg', 'awdeorio'),
    ('2ec7cf8ae158b3b1f40065abfb33e81143707842.jpg', 'jag');

INSERT INTO comments(owner, postid, text) VALUES
    ('awdeorio', 3, '#chickensofinstagram'),
    ('jflinn', 3, 'I <3 chickens'),
    ('michjc', 3, 'Cute overload!'),
    ('awdeorio', 2, 'Sick #crossword'),
    ('jflinn', 1, 'Walking the plank #chickensofinstagram'),
    ('awdeorio', 1, 'This was after trying to teach them to do a #crossword'),
    ('jag', 4, 'Saw this on the diag yesterday!');

INSERT INTO following(username1, username2) VALUES
    ('awdeorio', 'jflinn'),
    ('awdeorio', 'michjc'),
    ('jflinn', 'awdeorio'),
    ('jflinn', 'michjc'),
    ('michjc', 'awdeorio'),
    ('michjc', 'jag'),
    ('jag', 'michjc');
    
INSERT INTO likes(owner, postid) VALUES
    ('awdeorio', 1),
    ('michjc', 1),
    ('jflinn', 1),
    ('awdeorio', 2),
    ('michjc', 2),
    ('awdeorio', 3);
