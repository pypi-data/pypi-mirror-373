#!/usr/bin/env python3
"""POC to test out yearly tech landscape."""
import os
import os.path
import json
from kospex_core import Kospex, GitRepo
import kospex_utils as KospexUtils
from kospex_utils import KospexTimer
from kospex_git import KospexGit
import kospex_schema as KospexSchema
from kospex_query import KospexQuery, KospexData
from rich.console import Console
from sqlite_utils import Database

kospex = Kospex()
console = Console()

kd = KospexData(kospex.kospex_db)

console.log("Querying from start of year")

db = Database(memory=True)
table = db[KospexSchema.TBL_COMMIT_FILES]



with KospexTimer("Querying commit files") as timed:
    kd.select("*")
    kd.from_table(KospexSchema.TBL_COMMIT_FILES)
    kd.where("committer_when", ">=", "2025-01-01")
    #kd.limit(5)
    rows = kd.execute()
    table.insert_all(rows, alter=True)
    console.log(f"{len(rows)}")

console.log(timed)

summary_sql = f"""SELECT DISTINCT(_ext), SUM(additions) as additions, SUM(deletions) as deletions,
count(*) as commits, count(DISTINCT(_repo_id)) as repos FROM {KospexSchema.TBL_COMMIT_FILES}
GROUP BY _ext"""


with KospexTimer("In memory summary") as summary_timer:
    summary_results = db.query(summary_sql)
    for item in summary_results:
        console.log(item)
    #console.log(summary_results)

console.log(summary_timer)


console.log("About to query the year before 2025")



kd = KospexData(kospex.kospex_db)

with KospexTimer("Querying commit files") as timed:
    kd.select("*")
    kd.from_table(KospexSchema.TBL_COMMIT_FILES)
    kd.where("committer_when", ">=", "2024-01-01")
    kd.where("committer_when", "<=", "2025-01-01")
    #kd.limit(5)
    rows = kd.execute()
    console.log(f"{len(rows)}")


console.log(timed)



kd3 = KospexData(kospex.kospex_db)

console.log("About to query from year 2024")


with KospexTimer("Querying commit files") as timed:
    kd3.select("*")
    kd3.from_table(KospexSchema.TBL_COMMIT_FILES)
    kd3.where("committer_when", ">=", "2024-01-01")
    #kd.limit(5)
    rows = kd3.execute()
    console.log(f"{len(rows)}")

console.log(timed)
