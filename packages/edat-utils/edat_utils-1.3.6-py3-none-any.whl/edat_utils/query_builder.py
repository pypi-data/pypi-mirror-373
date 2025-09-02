import numbers
import re
from typing import List

from edat_utils.schema import EdatFilter, EdatOrder, EdatPagination


AND = " AND "
COMMA_SEPARARATOR = ", "


class EdatQueryBuilder:
    @staticmethod
    def build_query(
        table: str,
        filter: EdatFilter,
        fields: List[str],
        pagination: EdatPagination,
        orders: List[EdatOrder],
        grouped: bool,
    ):
        select = []
        where = []
        group = []
        pagination_text = ""
        orderBy = []

        for key in filter:
            value = filter[key]
            if isinstance(value, dict):
                for key_dict in list(value.keys()):
                    value_dict = EdatQueryBuilder.__get_value(value[key_dict])

                    match key:
                        case "eq":
                            where.append(key_dict + " = " + value_dict)
                        case "ne":
                            where.append(key_dict + " != " + value_dict)
                        case "like":
                            where.append(
                                "lower("
                                + key_dict
                                + ")"
                                + " LIKE "
                                + "lower('%"
                                + eval(value_dict)
                                + "%')"
                            )

                        case "likeTranslate":
                            _termo = (
                                "translate(lower('%"
                                + eval(value_dict)
                                + "%'),'áàâãäåaaaÁÂÃÄÅAAAÀéèêëeeeeeEEEÉEEÈìíîïìiiiÌÍÎÏÌIIIóôõöoooòÒÓÔÕÖOOOùúûüuuuuÙÚÛÜUUUUçÇñÑýÝ','aaaaaaaaaAAAAAAAAAeeeeeeeeeEEEEEEEiiiiiiiiIIIIIIIIooooooooOOOOOOOOuuuuuuuuUUUUUUUUcCnNyY')"
                            )
                            where.append(f"lower({key_dict}) LIKE {_termo}")

                        case "startWith":
                            where.append(
                                "lower("
                                + key_dict
                                + ")"
                                + " LIKE "
                                + "lower('"
                                + eval(value_dict)
                                + "%')"
                            )

                        case "startWithTranslate":
                            _termo = (
                                "translate(lower('"
                                + eval(value_dict)
                                + "%'),'áàâãäåaaaÁÂÃÄÅAAAÀéèêëeeeeeEEEÉEEÈìíîïìiiiÌÍÎÏÌIIIóôõöoooòÒÓÔÕÖOOOùúûüuuuuÙÚÛÜUUUUçÇñÑýÝ','aaaaaaaaaAAAAAAAAAeeeeeeeeeEEEEEEEiiiiiiiiIIIIIIIIooooooooOOOOOOOOuuuuuuuuUUUUUUUUcCnNyY')"
                            )
                            where.append(f"lower({key_dict}) LIKE {_termo}")

                        case "termsListTranslate":
                            _value_dict = f"{value_dict.strip().replace(' ', '%')}"
                            _termo = f"translate(lower('%{eval(_value_dict)}%'),'áàâãäåaaaÁÂÃÄÅAAAÀéèêëeeeeeEEEÉEEÈìíîïìiiiÌÍÎÏÌIIIóôõöoooòÒÓÔÕÖOOOùúûüuuuuÙÚÛÜUUUUçÇñÑýÝ','aaaaaaaaaAAAAAAAAAeeeeeeeeeEEEEEEEiiiiiiiiIIIIIIIIooooooooOOOOOOOOuuuuuuuuUUUUUUUUcCnNyY')"
                            where.append(f"lower({key_dict}) LIKE {_termo}")

                        case "isNull":
                            where.append(key_dict + " IS NULL ")
                        case "notNull":
                            where.append(key_dict + " IS NOT NULL ")
                        case "in":
                            where.append(key_dict + " IN " + value_dict)
                        case "notIn":
                            where.append(key_dict + " NOT IN " + value_dict)
                        case "lt":
                            where.append(key_dict + " < " + value_dict)
                        case "lte":
                            where.append(key_dict + " <= " + value_dict)
                        case "gt":
                            where.append(key_dict + " > " + value_dict)
                        case "gte":
                            where.append(key_dict + " >= " + value_dict)

                        case "or_":
                            or_clauses = []
                            for subfilter in value:  # lista de dicts
                                sub_conditions = []
                                for subkey, subval in subfilter.items():
                                    val = EdatQueryBuilder.__get_value(subval)
                                    if isinstance(subval, list):
                                        sub_conditions.append(f"{subkey} IN {val}")
                                    else:
                                        sub_conditions.append(f"{subkey} = {val}")
                                or_clauses.append(
                                    "(" + " AND ".join(sub_conditions) + ")"
                                )
                            where.append("(" + " OR ".join(or_clauses) + ")")

                        case "or":
                            or_clauses = []
                            for subfilter in value:  # value é uma lista de dicts
                                sub_conditions = []
                                for subkey, subval in subfilter.items():
                                    val = EdatQueryBuilder.__get_value(subval)
                                    if isinstance(subval, list):
                                        sub_conditions.append(f"{subkey} IN {val}")
                                    else:
                                        sub_conditions.append(f"{subkey} = {val}")
                                or_clauses.append(
                                    "(" + " AND ".join(sub_conditions) + ")"
                                )
                            where.append("(" + " OR ".join(or_clauses) + ")")

                        case _:
                            where.append(key_dict + " = " + value_dict)
            else:
                where.append(key + " = " + str(value))

        if grouped:
            select.append("SUM(contador) as contador")
            for field in fields:
                if field == "contador":
                    continue
                underline_field = re.sub(r"(?<!^)(?=[A-Z])", "_", field).lower()
                select.append(underline_field)
                group.append(underline_field)
        else:
            for field in fields:
                if field == "contador":
                    continue
                underline_field = re.sub(r"(?<!^)(?=[A-Z])", "_", field).lower()
                select.append(underline_field)

        if pagination:
            if pagination.limit and pagination.limit != 0:
                pagination_text = f"{pagination_text} LIMIT {str(pagination.limit)}"
            if pagination.offset and pagination.offset != 0:
                pagination_text = f"{pagination_text} OFFSET {str(pagination.offset)}"

        if orders:
            for order in orders:
                underline_field = re.sub(r"(?<!^)(?=[A-Z])", "_", order.field).lower()
                orderBy.append(underline_field + " " + order.type.value)

        query = "SELECT "
        query = query + COMMA_SEPARARATOR.join(select)
        query = query + " FROM " + table
        if where:
            query = query + " WHERE " + AND.join(where)
        if group:
            query = query + " GROUP BY " + COMMA_SEPARARATOR.join(group)
        if orderBy:
            query = query + " ORDER BY " + COMMA_SEPARARATOR.join(orderBy)
        query = query + pagination_text

        return query

    @staticmethod
    def __get_value(value):
        date_pattern_str = r"^\d{4}-\d{2}-\d{2}$"
        if isinstance(value, numbers.Number):
            return str(value)
        elif isinstance(value, str):
            if re.match(date_pattern_str, value):
                return "date '" + value + "'"
            else:
                return "'" + value + "'"
        elif isinstance(value, list) or isinstance(value, dict):
            if isinstance(value[0], str):
                return "('" + "', '".join(value) + "')"
            else:
                return "(" + ", ".join(map(str, value)) + ")"
        else:
            return value
