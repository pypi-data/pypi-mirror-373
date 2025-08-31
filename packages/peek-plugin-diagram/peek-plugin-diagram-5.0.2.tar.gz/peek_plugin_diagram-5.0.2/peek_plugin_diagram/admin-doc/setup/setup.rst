Setup Tasks
-----------

Enabling Edit Support
`````````````````````

Setting Default Level

Run the following SQL where "1" is the level ::

    UPDATE pl_diagram."ModelCoordSet" as dummy
    SET "editDefaultLevelId"=sq.id
    FROM (SELECT id, "coordSetId"
          from pl_diagram."DispLevel"
          where "order" = 1) AS sq
    WHERE dummy.id=sq."coordSetId";
