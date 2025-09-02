QUERY = """
DO $$
DECLARE
    v_id UUID;
    v_capability_id CHAR(32);
    v_role_id CHAR(32);
    v_application_name TEXT := '{application_name}';
BEGIN
    FOR v_capability_id IN
        SELECT c.id
        FROM capability c
        JOIN "route" r ON r.id = c.route_id
        JOIN "application" a ON a.id = c.application_id
        WHERE a."name" = v_application_name
          AND concat(r.url, ' - ', r."method") IN (
              ''
              {url_methods}
          )
    LOOP
        BEGIN
            -- Obtenha role_id
            SELECT id INTO v_role_id
            FROM "role"
            WHERE upper("name") = upper('{role_name}');

            -- Insira na tabela policy
            INSERT INTO public."policy" (id, active, created_at, tag, capability_id, role_id)
            VALUES (md5((random())::text), TRUE, now(), '#INSERIDO_VIA_SCRIPT', v_capability_id, v_role_id);

        EXCEPTION WHEN OTHERS THEN
            -- Ignore o erro e continue
            RAISE NOTICE 'Erro ao inserir capability_id na policy%: %', v_capability_id, SQLERRM;
        END;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

"""  # noqa

QUERY_FILTER = ", '{url} - {method}'"  # noqa
