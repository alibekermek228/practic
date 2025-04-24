-- Создание таблицы
CREATE TABLE IF NOT EXISTS phonebook (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL
);

-- Функция поиска по шаблону
CREATE OR REPLACE FUNCTION search_by_pattern(pattern TEXT)
RETURNS TABLE(id INT, name VARCHAR, phone VARCHAR)
AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM phonebook
    WHERE name ILIKE '%' || pattern || '%'
       OR phone ILIKE '%' || pattern || '%';
END;
$$ LANGUAGE plpgsql;

-- Процедура вставки или обновления
CREATE OR REPLACE PROCEDURE insert_or_update_user(p_name TEXT, p_phone TEXT)
AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phonebook WHERE name = p_name) THEN
        UPDATE phonebook SET phone = p_phone WHERE name = p_name;
    ELSE
        INSERT INTO phonebook(name, phone) VALUES (p_name, p_phone);
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Массовая вставка с проверкой
CREATE OR REPLACE PROCEDURE bulk_insert_users(p_names TEXT[], p_phones TEXT[], OUT invalid_data TEXT[])
AS $$
DECLARE
    i INT;
    valid_phone_pattern TEXT := '^[0-9]{10,15}$';
BEGIN
    invalid_data := ARRAY[]::TEXT[];

    FOR i IN 1 .. array_length(p_names, 1) LOOP
        IF p_phones[i] ~ valid_phone_pattern THEN
            CALL insert_or_update_user(p_names[i], p_phones[i]);
        ELSE
            invalid_data := array_append(invalid_data, p_names[i] || ':' || p_phones[i]);
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Функция постраничного вывода
CREATE OR REPLACE FUNCTION get_phonebook_page(p_limit INT, p_offset INT)
RETURNS TABLE(id INT, name VARCHAR, phone VARCHAR)
AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM phonebook
    ORDER BY id
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;

-- Процедура удаления по имени или телефону
CREATE OR REPLACE PROCEDURE delete_by_name_or_phone(p_value TEXT)
AS $$
BEGIN
    DELETE FROM phonebook
    WHERE name = p_value OR phone = p_value;
END;
$$ LANGUAGE plpgsql;

