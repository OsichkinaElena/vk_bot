create table if not exists users (
id serial primary key,
user_id int unique);
create table if not exists featured_users (
id serial primary key,
user_id int, 
id_user int references users(id));
