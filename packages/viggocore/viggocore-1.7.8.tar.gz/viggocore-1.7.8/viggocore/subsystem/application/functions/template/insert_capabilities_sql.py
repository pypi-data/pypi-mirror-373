QUERY = """
DO $$ 
DECLARE
    v_route_id CHAR(32);
    v_application_id CHAR(32);
    v_application_name TEXT := '{application_name}';
BEGIN
    -- Obtenha application_id uma vez, pois é constante
    SELECT id INTO v_application_id
    FROM "application"
    WHERE "name" = v_application_name;

    FOR v_route_id IN 
        SELECT r.id
        FROM route r
        WHERE concat(r.url, ' - ', r."method") IN (
            ''
            {url_methods}
        )
    LOOP
        BEGIN
            -- Insira na tabela capability
            INSERT INTO capability (id, active, created_at, tag, route_id, application_id)
            VALUES (md5((random())::text), TRUE, now(), '#INSERIDO_VIA_SCRIPT', v_route_id, v_application_id);

        EXCEPTION WHEN OTHERS THEN
            -- Ignore o erro e continue
            RAISE NOTICE 'Erro ao inserir route_id %: % na capability', v_route_id, SQLERRM;
        END;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
"""  # noqa

QUERY_FILTER = ", '{url} - {method}'"  # noqa
