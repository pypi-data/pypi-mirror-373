import sqlite3

conn = sqlite3.connect("91172C7W501-051_R05_FC.db")

entity_id = 162200
cursor = conn.cursor()

cursor.execute(f"""
                SELECT distinct child.*
                FROM step_arguments args
                    JOIN step_entities child ON args.value_text = child.id
                WHERE args.entity_id = {entity_id} AND args.value_type = 'reference'

                UNION
                
                SELECT distinct child2.*
                FROM step_arguments args1
                    JOIN step_arguments args2 ON args2.entity_id = args1.value_text
                    JOIN step_entities child2 ON args2.value_text = child2.id
                WHERE args1.entity_id = {entity_id} AND args1.value_type = 'reference' AND args2.value_type = 'reference'

                UNION
                
                SELECT distinct child3.*
                FROM step_arguments args1
                    JOIN step_arguments args2 ON args2.entity_id = args1.value_text
                    JOIN step_arguments args3 ON args3.entity_id = args2.value_text
                    JOIN step_entities child3 ON args3.value_text = child3.id
                WHERE args1.entity_id = {entity_id} AND args1.value_type = 'reference' AND args2.value_type = 'reference' AND args3.value_type = 'reference'

                UNION
                
                SELECT distinct child4.*
                FROM step_arguments args1
                    JOIN step_arguments args2 ON args2.entity_id = args1.value_text
                    JOIN step_arguments args3 ON args3.entity_id = args2.value_text
                    JOIN step_arguments args4 ON args4.entity_id = args3.value_text
                    JOIN step_entities child4 ON args4.value_text = child4.id
                WHERE args1.entity_id = {entity_id} AND args1.value_type = 'reference' AND args2.value_type = 'reference' AND args3.value_type = 'reference' AND args4.value_type = 'reference'
                """)

print(cursor.fetchall())

cursor.execute(f"""
                SELECT distinct args.*
                FROM step_arguments args
                WHERE args.entity_id = {entity_id}

                UNION
                
                SELECT distinct args2.*
                FROM step_arguments args1
                    JOIN step_arguments args2 ON args2.entity_id = args1.value_text
                WHERE args1.entity_id = {entity_id} AND args1.value_type = 'reference'

                UNION
                
                SELECT distinct args3.*
                FROM step_arguments args1
                    JOIN step_arguments args2 ON args2.entity_id = args1.value_text
                    JOIN step_arguments args3 ON args3.entity_id = args2.value_text
                WHERE args1.entity_id = {entity_id} AND args1.value_type = 'reference' AND args2.value_type = 'reference'

                UNION
                
                SELECT distinct args4.*
                FROM step_arguments args1
                    JOIN step_arguments args2 ON args2.entity_id = args1.value_text
                    JOIN step_arguments args3 ON args3.entity_id = args2.value_text
                    JOIN step_arguments args4 ON args4.entity_id = args3.value_text
                WHERE args1.entity_id = {entity_id} AND args1.value_type = 'reference' AND args2.value_type = 'reference' AND args3.value_type = 'reference'
                """)

print(cursor.fetchall())