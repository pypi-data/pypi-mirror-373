## INSTALL
```bash
# Create python virtual environment
python3 -m venv venv
# Activate this environment
source venv/bin/activate
# Install dependencies
pip install -r requirements.dev.txt

# Create pg db
createdb --U username -W dbname
## set password for db user

# Copy .env file from sample template
cp .env.sample .env
## set your pg creds in .env file
```

## TEST
```bash
pytest
```


### pre-commit
You can done `commit` only after `pytest` will done success.
Pre-commit script stored in `.git/hooks/pre-commit` file; current script is:
```shell
#!/bin/sh
pytest
```

### Relations
```mermaid
classDiagram
direction BT
class Agent {
   timestamp(0) with time zone created_at
   timestamp(0) with time zone updated_at
   integer exid
   jsonb auth
   smallint ex_id
   bigint user_id
   integer id
}
class Asset {
   smallint type_  /* spot: 1\nearn: 2\nfound: 3 */
   double precision free
   double precision freeze
   double precision lock
   double precision target
   integer agent_id
   smallint coin_id
   integer id
}
class Coin {
   varchar(15) ticker
   double precision rate
   boolean is_fiat
   smallint id
}
class CoinEx {
   varchar(31) exid
   boolean p2p
   smallint coin_id
   smallint ex_id
   integer id
}
class Cur {
   varchar(3) ticker
   double precision rate
   smallint id
}
class CurEx {
   varchar(31) exid
   boolean p2p
   smallint cur_id
   smallint ex_id
   integer id
}
class Ex {
   varchar(31) name
   varchar(63) host  /* With no protocol 'https://' */
   varchar(63) host_p2p  /* With no protocol 'https://' */
   varchar(63) url_login  /* With no protocol 'https://' */
   smallint type_  /* p2p: 1\ncex: 2\nmain: 3\ndex: 4\nfutures: 8 */
   varchar(511) logo
   smallint id
}
class Fiat {
   varchar(127) detail
   varchar(127) name
   double precision amount
   double precision target
   integer pmcur_id
   bigint user_id
   integer id
}
class FiatEx {
   integer exid
   smallint ex_id
   integer fiat_id
   integer id
}
class Limit {
   integer amount
   integer unit
   integer level
   boolean income
   bigint added_by_id
   integer pmcur_id
   integer id
}
class Pm {
   varchar(63) name
   smallint rank
   smallint type_  /* bank: 0\nweb_wallet: 1\ncash: 2\ngift_card: 3\ncredit_card: 4 */
   varchar(127) logo
   boolean multiAllow
   integer id
}
class PmCur {
   smallint cur_id
   integer pm_id
   integer id
}
class PmCurEx {
   boolean blocked
   smallint ex_id
   integer pmcur_id
   integer id
}
class PmEx {
   varchar(31) exid
   smallint ex_id
   integer pm_id
   integer id
}
class User {
   timestamp(0) with time zone created_at
   timestamp(0) with time zone updated_at
   smallint role  /* READER: 4\nWRITER: 2\nMANAGER: 6\nADMIN: 7 */
   smallint status  /* CREATOR: 5\nADMINISTRATOR: 4\nMEMBER: 3\nRESTRICTED: 2\nLEFT:... */
   varchar(95) username
   bigint ref_id
   bigint id
}

Agent  -->  Ex : ex_id-id
Agent  -->  User : user_id-id
Asset  -->  Agent : agent_id-id
Asset  -->  Coin : coin_id-id
CoinEx  -->  Coin : coin_id-id
CoinEx  -->  Ex : ex_id-id
CurEx  -->  Cur : cur_id-id
CurEx  -->  Ex : ex_id-id
Fiat  -->  PmCur : pmcur_id-id
Fiat  -->  User : user_id-id
FiatEx  -->  Ex : ex_id-id
FiatEx  -->  Fiat : fiat_id-id
Limit  -->  PmCur : pmcur_id-id
Limit  -->  User : added_by_id-id
PmCur  -->  Cur : cur_id-id
PmCur  -->  Pm : pm_id-id
PmCurEx  -->  Ex : ex_id-id
PmCurEx  -->  PmCur : pmcur_id-id
PmEx  -->  Ex : ex_id-id
PmEx  -->  Pm : pm_id-id
User  -->  User : ref_id-id
```