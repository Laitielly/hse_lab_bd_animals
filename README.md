# Laboratory work on the discipline database of the HSE University. 
**Performed by 3rd year students Anna Sidorova (work on the database structure) and Vladislav Budilin (an app part).**

Let's go through the conditions of laboratory work and simultaneously understand what kind of database it is, why and how it works.

## Come up with your own subject area and think over the database schema for it.

While searching for the subject area, we thought about poor abandoned animals.

Unfortunately, there are now many irresponsible owners in the world who, in case of illness or needlessness, simply throw animals out into the street. It would be ideal if private organizations or the state would think about animal centers where each animal would have a unique chip.

If the owner loses the animal or it has been proven that he intentionally threw it away, then sanctions will be applied to him or her. After all, this database stores information about the buyer, his purchase and about the center where this animal was located (so that it could return to its usual environment).

The form of buying an animal is very serious - the buyer is required to have his or her passport and personal phone number. That is why the punishment will reach the guilty.

Accordingly, we have two schemes (simpler and crow's feet):

![Скрин1](https://github.com/Laitielly/hse_lab_bd_animals/blob/main/images/scbase.png)
![Скрин2](https://github.com/Laitielly/hse_lab_bd_animals/blob/main/images/crow's_feet_animals.png)

## Highlight the functional requirements for your database.

### Functional data requirements.
  - The following information is stored in the table about animals:
      - stamp this number containing 6 positions (000001, 134510) is unique and cannot be repeated. Contains information about the animal's chip.
      - species is a text variable that must be specified. Species contains information about the type of animal: dog, cat, wolf, etc.
      - breed is a text variable that must be specified. Breed contains information about the breed of the animal: akita, Siamese, mongrel, etc.
      - age - integer, which must be at least zero. Age contains information about the age of the animal in months.
      - collars - a text variable that must be specified. Colors contains information about the color of the animal.
      - sex is a text variable that must be specified. Sex contains information about the sex of the animal.
      - price - a number whose upper bound is 10^10 and may contain pennies. 
      - taken is a Boolean variable that carries information about whether an animal was bought or not.
      - shop id - the foreign key of the store table. Contains information about where the animal is located, if it was not bought or where it was before the purchase.

  - The following information is stored in the table about shop:
      - id - the internal identifier of the shop, can not exceed 10^6. Defined by the user.
      - name - a text variable that must be specified. Contains the name of the shop.
      - district - a text variable that must be specified. Contains information about the shop's address.
      - phone - not an empty field, contains the phone number (xxx-xxx-xx-xx).

  - The following information is stored in the table about buyer:
      - passport - the buyer's passport is unique, it must be.
      - name - a text variable that must be specified. Contains the full name of the buyer.
      - phone - not an empty field, contains the phone number (xxx-xxx-xx-xx).
      - discount is an integer variable not exceeding 100 and not less than 0. It contains information about the buyer's discount.

  - The following information is stored in the purchase table:
      - id - id of the purchase - unique, must be, does not exceed 10 ^ 6.
      - dat - the date of purchase made by the buyer.
      - price - a number whose upper bound is 10^10 and may contain pennies. Taken into account with the buyer's discount.
      - stamp - a foreign key indicating the animal that was purchased. Must be unique in the purchase table.
      - idbuyer - a foreign key indicating the ID of the buyer who bought the animal. Must be.

One animal can be bought several times if the previous owner died or failed to cope with his responsibility. Then the previous purchase is deleted and a new one is created.

The buyer can buy several animals.

A store can store multiple animals, but an animal can only be in 1 store.

### Functional requirements for operations.
(For more information about function and procedure calls, see logs_database.sql)
The database has the following functions and procedures:
  - INSERT functions: **insert_animal, insert_shop, insert_buyer, insert_purchase** - functions adding NEW data to the tables following from the function names.
  - **print_table** - outputs all rows from the table specified to it when calling.
  - CLEAR functions: **clear_table, clear_all_tables** - the first function clears ALL data from the table specified when calling, the second clears ALL data from ALL tables.
  - DELETE functions:
    - **delete_row** - deleting a line from the specified one when calling the table of a certain specified id.
    - **delete_buyer_by_phone** - deleting a customer by their phone number.
    - **delete_purchase_by_stamp_phone** - delete a purchase by the animal's chip and the buyer's phone number.
    - **delete_shop_by_location** - delete a store at its address.
  - FIND functions:
    - **find_animal_by_phenotype** - search for an animal by its type, breed, color.
    - **find_buyer_by_phone** - search for a buyer by his phone number.
    - **find_shop_by_location_name** - search for a store by its address.
    - **find_purchase_by_stamp** - find a purchase by the chip of the purchased animal.
    - **find_with_id** - search for any ID data from the specified table when calling the function.
    - **find_not_bought** - search for purchased or not purchased animals.
  - UPDATE functions:
    - **update_animal_by_stamp** - update by chip data in the animals table.
    - **update_buyer_by_passport** - update the buyer's data on his or her passport.
    - **update_purchase_by_id** - update purchase data via the purchase ID.
    - **update_shop_by_id** - update store data via store ID.
 
 ## Implement a relational database for your subject area (all tables must be at least in the third normal form) - check.
 ## DB criteria:
  - The database must be in the third normal form or higher - check.
  - The minimum number of tables is 4 - check.
  - All connections from the GUI must be made by a dedicated, non-root, user:
      You can read more about the users in users.txt. In short, we have 2 users - one creates a database and gives rights to it to the client (both are not the root users), and the second uses a database created by creator. Accordingly, the item is executed. Creator performs all actions through the logs database created earlier, where the original functions of working with authorization and creating the animals database are stored. Connects to animals only if the client is granted rights.
  - There must be at least one index created by you for the selected text non-key field.
    There are 2 indexes created here: 
      - find_by_phenotype for finding and deleting an animal by phenotype; 
      - find_by_phone for quickly finding and deleting a buyer.
  - One of the tables must have a field that is filled in/changed only by the trigger.
    There are 2 triggers created here: 
      - price_with_disc with function counter_function - before updating the purchase table, the price is calculated taking into account the discount.
      - is_bought with function bought_animal - after adding, changing or deleting a purchase, the status of the animal changes to purchased or not, depending on the operation.
 ## Implement a GUI program with the following functionality:
  - Creating a database - check;
  - Deleting a database - check;
  - Output of table contents - check;
  - Cleaning (partial - one, and full - all) tables - check;
  - Adding new data - check;
  - Search by a pre-selected (by you) text non-key field - check;
  - Updating the tuple - check;
  - Deleting by a pre-selected text non-key field - check;
  - Deleting a specific record selected by the user - check;
  - All functions must be implemented as stored procedures - check.

## Data entry examples:

```
select insert_shop(100001, '4 лапы', 'Советский Бекетова 8', 9000000000);
select insert_shop(100002, 'Зоопторг', 'Автозавод Львовская 22', 9800000000);
select insert_shop(100003, 'Багира', 'Ленинский Кировская 9', 9810000000);
select insert_shop(100004, 'Шапиро', 'Нижегородский Родионова 16', 9820000000);
select insert_shop(100005, 'Коты и собаки', 'Сормовский Баренца 4', 9830000000);
select insert_shop(100006, 'Феликс', 'Советский Бринского 18', 9840000000);
select insert_shop(100007, 'Кошкин дом', 'Советский Лядова 32', 9850000000);
select insert_shop(100008, 'Домовенок', 'Нижегородский Деловая 1', 9860000000);
select insert_shop(100009, 'Животные', 'Ленинский Ленина 108', 9870000000);
select insert_shop(100010, 'Хохотушки лапатушки', 'Ленинский Счастливая 2', 9880000000);

select insert_buyer(1, 'Иванова Дарья',	9876543212,	15);
select insert_buyer(10, 'Кириенко Евгений',	9876543213,	10);
select insert_buyer(11, 'Саламонова Екатерина',	9876543214,	30);
select insert_buyer(21, 'Красавчик Михаил',	9876543215,	0);
select insert_buyer(31, 'Милый Димон',	9876543216,	12);
select insert_buyer(41, 'Навороченная Евгения',	9876543217,	15);
select insert_buyer(51, 'Димыч Дим',	9876543218,	5);
select insert_buyer(61, 'Полотенцева Светлана',	9876543219,	0);
select insert_buyer(71,	'Житие Мое',	9876543220,	5);
select insert_buyer(81,	'Гордиенко Максим',	9876543221,	30);

select insert_animal(1, 'собака', 'акита', 3, 'рыжий', 'мужской', 35000, 100009);
select insert_animal(2, 'собака', 'дворняжка', 12, 'черный', 'женский', 15000, 100001);
select insert_animal(3, 'кот', 'сиамский', 4, 'пепельный', 'мужской', 10000, 100002);
select insert_animal(4, 'кот', 'дворняжка', 6, 'рыжий', 'женский', 5000, 100003);
select insert_animal(5, 'лемур', 'кошачий', 7, 'серый', 'мужской', 50000, 100004);
select insert_animal(6, 'белка', 'золотистобрюхая', 2, 'темно рыжий', 'мужской', 13000, 100005);
select insert_animal(7, 'волк', 'дикий', 24, 'серый', 'женский', 20000, 100006);
select insert_animal(8, 'тигр', 'амурский', 2, 'рыжий', 'женский', 100000, 100007);
select insert_animal(9, 'лев', 'сенегальский', 2, 'рыжий', 'мужской', 150000, 100009);
select insert_animal(10, 'кошкодевочка', '2D', 216, 'брюнетка', 'женский', 1000000, 100008);

select insert_purchase(1, '2018-01-12', 1, 1);
select insert_purchase(2, '2002-02-12', 2, 10);
select insert_purchase(3, '2022-12-02', 3, 11);
select insert_purchase(4, '2008-07-22', 4, 21);
select insert_purchase(5, '2008-08-13', 5, 31);
```
