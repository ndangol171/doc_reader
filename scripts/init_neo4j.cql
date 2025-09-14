
CREATE CONSTRAINT indicator_value IF NOT EXISTS
FOR (i:Indicator) REQUIRE (i.value) IS UNIQUE;
CREATE INDEX indicator_type IF NOT EXISTS FOR (i:Indicator) ON (i.type);
CREATE CONSTRAINT document_url IF NOT EXISTS
FOR (d:Document) REQUIRE (d.url) IS UNIQUE;
CREATE CONSTRAINT campaign_name IF NOT EXISTS
FOR (c:Campaign) REQUIRE (c.name) IS UNIQUE;
