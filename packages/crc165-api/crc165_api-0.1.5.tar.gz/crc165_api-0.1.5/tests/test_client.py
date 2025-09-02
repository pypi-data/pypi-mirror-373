import requests
import re
import json
import pandas as pd
import os
# The simple REST API client for MatInf VRO API
class MatInfWebApiClient:
    def __init__(self, service_url, api_key):
        self.service_url = service_url + "/vroapi/v1/"
        self.api_key = api_key
        self.file_name=""
        self.dataframe=None

    def getFilename_fromCd(self, cd):
        if not cd:
            return None
        fname = re.findall('filename=(.+)(?:;.+)', cd)
        if len(fname) == 0:
            return None
        self.file_name=fname[0]
        return fname[0]

    def get_headers(self):
        return { 'VroApi': self.api_key }

    def execute(self, sql):
        headers = self.get_headers()
        data = { 'sql': sql }
        try:
            response = requests.post(self.service_url+"execute", headers=headers, data=data)
            response.raise_for_status()  # Raise exception for non-2xx status codes
            js = response.json()
            self.dataframe = pd.DataFrame.from_dict(js)
            self.dataframe
            return js
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None
        
    def get_filtered_objects(self, associated_typenames, main_object, start_date, end_date, creator=None, strict=False):
        typename_str = ", ".join(f"'{typename}'" for typename in associated_typenames)

        # Start query
        query = f"""
        SELECT 
            o.objectid AS main_objectid, 
            o.objectname,
            t.typename AS main_object,
            o._created AS created_date,
            o._updated AS updated_date,
            o.objectfilepath AS main_objectfilepath,
            u.username AS creator_username,
            u.email AS creator_email,
            linked_oi.objectid AS linked_objectid,
            linked_oi.objectfilepath AS linked_objectfilepath,
            ti.typename AS associated_typename,
            u_link.email AS linked_creator_email
        FROM vroObjectinfo o
        JOIN vroTypeinfo t ON o.typeid = t.typeid
        JOIN vroAspnetusers u ON o._createdBy = u.id
        JOIN vroObjectlinkobject olo ON o.objectid = olo.objectid
        JOIN vroObjectinfo linked_oi ON olo.linkedobjectid = linked_oi.objectid
        JOIN vroTypeinfo ti ON linked_oi.typeid = ti.typeid
        JOIN vroAspnetusers u_link ON linked_oi._createdBy = u_link.id
        WHERE t.typename = '{main_object}'
        AND o._created BETWEEN '{start_date}' AND '{end_date}'
    """

        # Optional creator filter
        if creator:
            query += f" AND (u.username = '{creator}' OR u.email = '{creator}')"

        query += " ORDER BY o.objectid;"

        result = self.execute(query)
        df = pd.DataFrame(result)

        if df.empty:
            return df, {}, []

        if strict:
            required_typenames = set(associated_typenames)
            grouped = df.groupby("main_objectid")
            valid_object_ids = []

            for obj_id, group in grouped:
                associated_types = set(group["associated_typename"])
                if required_typenames.issubset(associated_types):
                    valid_object_ids.append(obj_id)

            df = df[df["main_objectid"].isin(valid_object_ids)]

            if df.empty:
                print("After strict filtering, no objects matched all required types.")

            object_link_mapping = (
                df[df["associated_typename"].isin(associated_typenames)]
                .groupby("main_objectid")["linked_objectid"]
                .apply(list)
                .to_dict()
            )
        else:
            object_link_mapping = df.groupby("main_objectid")["linked_objectid"].apply(list).to_dict()

        object_ids = df["main_objectid"].unique().tolist()
        return df, object_link_mapping, object_ids


    
    def filter_samples_by_elements(self, object_ids, element_criteria):
        """
        Filters samples based on element names and percentage range.
        """
        if not object_ids:
            print("No objects found in the previous step.")
            return pd.DataFrame()

        # Remove duplicates
        unique_object_ids = list(set(object_ids))


        if not unique_object_ids:
            print("Error: No valid object IDs found. Skipping query.")
            return pd.DataFrame()

        # Convert list to comma-separated string for SQL query
        object_ids_str = ", ".join(map(str, unique_object_ids))
  
        query = f"""
        SELECT 
            s.sampleid, 
            s.elemnumber, 
            s.elements
        FROM vroSample s
        WHERE s.sampleid IN ({object_ids_str});
        """
        # Execute query
        result = self.execute(query)

        # Check if API returned None or empty data
        if not result:
            print("Error: API returned None or empty response.")
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(result)
        df["elements"] = df["elements"].astype(str)

        # Filter samples based on required elements and optional percentage range
        required_elements = set(element_criteria.keys())
        
        filtered_df = df[df["elements"].apply(lambda x: bool(required_elements & set(x.strip("-").split("-"))))]
        sample_ids = filtered_df["sampleid"].tolist()
        return filtered_df, sample_ids

    def filter_samples_by_elements_and_composition(self, sample_ids, object_link_mapping, element_criteria):
        """
        Filters samples based on element names and percentage range, including linked Composition objects.
        Then, filters object_link_mapping based on the final filtered DataFrame.
        Skips filtering for samples without linked composition-type objects.
        """
        print("\n--- Starting element composition filtering ---")

        if not sample_ids:
            print("No objects found in the previous step.")
            return pd.DataFrame(), {}

        unique_sample_ids = set(sample_ids)

        # Filter mapping to keep only relevant sample IDs
        filtered_mapping = {k: v for k, v in object_link_mapping.items() if k in unique_sample_ids}

        if not filtered_mapping:
            print("No matching samples found in the mapping. Skipping query.")
            return pd.DataFrame(), {}

        # Flatten linked object IDs
        linked_object_ids = set(val for sublist in filtered_mapping.values() for val in sublist)

        if not linked_object_ids:
            print("No linked object IDs found. Skipping query.")
            return pd.DataFrame(), {}

        linked_object_ids_str = ", ".join(map(str, linked_object_ids))
        print(linked_object_ids_str)
        if not linked_object_ids_str.strip():
            print("Linked object ID string is empty. Skipping composition query.")
            return pd.DataFrame(), {}

        # Step 2: Query Composition table for element percentages
        query_composition = f"""
        SELECT sampleid, elementname, valuepercent
        FROM vroComposition
        WHERE sampleid IN ({linked_object_ids_str});
        """

        try:
            composition_result = self.execute(query_composition)
            
        except Exception as e:
            print(f"Error executing composition query: {e}")
            return pd.DataFrame(), {}

        if not composition_result:
            print("Error: No composition data found.")
            return pd.DataFrame(), {}

        df = pd.DataFrame(composition_result)

        if df.empty:
            print("Warning: No matching composition data found.")
            return pd.DataFrame(), {}

        # Debug print of available composition data
        print("\nAvailable composition data (sample):")
        print(df.head(10))

        # Normalize and apply filters
        df["elementname"] = df["elementname"].str.strip().str.lower()
        element_criteria = {k.lower(): v for k, v in element_criteria.items()}

        filter_condition = None
        print("\nApplying element criteria:")

        for element, value_range in element_criteria.items():
            if not value_range:
                print(f"- Skipping percentage filter for element: {element} (only presence required)")
                condition = df["elementname"] == element
            else:
                min_val, max_val = value_range
                print(f"- Filtering for element: {element} in range [{min_val}, {max_val}]")
                condition = (
                    (df["elementname"] == element) &
                    (df["valuepercent"] >= min_val) &
                    (df["valuepercent"] <= max_val)
                )

            matching = df[condition]
            print(f"  -> Matching rows for '{element}': {len(matching)}")

            filter_condition = condition if filter_condition is None else filter_condition | condition

        if filter_condition is not None:
            df = df[filter_condition]

        #print(f"\nFiltered composition entries after applying criteria: {len(df)}")

        matched_sample_ids = set(df["sampleid"].unique())

        print(f"\nMatched sample IDs: {matched_sample_ids}")

        # Final mapping: keep only those linked objects that are matched in composition
        final_filtered_mapping = {
            k: [obj_id for obj_id in v if obj_id in matched_sample_ids]
            for k, v in filtered_mapping.items()
        }

        # Remove entries with no valid links left
        final_filtered_mapping = {k: v for k, v in final_filtered_mapping.items() if v}

        print(f"\nFinal number of samples after filtering: {len(final_filtered_mapping)}")
        return df, final_filtered_mapping

    def get_summary(self, main_object="Sample", start_date="2000-01-01", end_date="2100-01-01",
                    include_associated=True, include_properties=True, include_composition=True,
                    include_linked_properties=True, property_names=None, required_elements=None,
                    required_properties=None, user_associated_typenames=None, creator=None,
                    save_to_json=False, save_to_csv=False, output_folder="."):


        print(f"\n Running summary for '{main_object}' from {start_date} to {end_date}...")

        # Step 1: Sample Query
        where_clause = f"WHERE t.typename = '{main_object}' AND o._created BETWEEN '{start_date}' AND '{end_date}'"
        if creator:
            where_clause += f" AND (u.email = '{creator}' OR u.username = '{creator}')"

        # Full query
        sample_query = f"""
        SELECT s.sampleid AS objectid, s.elements, s.elemnumber,
            o.objectname, o.objectfilepath, o._created AS created_date,
            u.username AS created_by, u.email AS creator_email
        FROM vroSample s
        JOIN vroObjectinfo o ON s.sampleid = o.objectid
        JOIN vroTypeinfo t ON o.typeid = t.typeid
        JOIN vroAspnetusers u ON o._createdBy = u.id
        {where_clause}
        """

        sample_data = self.execute(sample_query)
        if not sample_data:
            print("No sample data returned.")
            return []

        df = pd.DataFrame(sample_data)
        print(f"Total samples retrieved: {len(df)}")

        df["elements_list"] = df["elements"].astype(str).apply(lambda x: x.strip("-").split("-"))
        df["nelements"] = df["elements_list"].apply(len)
        object_ids = df["objectid"].tolist()
        object_ids_str = ", ".join(map(str, object_ids))

        # Step 2: Associated Objects
        grouped_assoc, assoc_df = {}, pd.DataFrame()
        if include_associated:
            assoc_query = f"""
            SELECT o.objectid, 
                linked_oi.objectid AS linked_objectid,
                linked_oi.objectname AS linked_objectname,
                linked_oi.objectfilepath AS linked_objectfilepath,
                linked_oi._created AS linked_created_date,
                linked_oi._updated AS linked_updated_date,
                ti.typename AS associated_typename
            FROM vroObjectlinkobject olo
            JOIN vroObjectinfo o ON o.objectid = olo.objectid
            JOIN vroObjectinfo linked_oi ON olo.linkedobjectid = linked_oi.objectid
            JOIN vroTypeinfo ti ON linked_oi.typeid = ti.typeid
            WHERE o.objectid IN ({object_ids_str})
            """
            assoc_data = self.execute(assoc_query)
            assoc_df = pd.DataFrame(assoc_data) if assoc_data else pd.DataFrame()
            print(f"Associated object links retrieved: {len(assoc_df)}")

            if not assoc_df.empty:
                grouped_assoc = assoc_df.groupby("objectid", group_keys=False).apply(
                    lambda g: [
                        {
                            "linked_objectid": row["linked_objectid"],
                            "linked_objectname": row["linked_objectname"],
                            "linked_objectfilepath": row["linked_objectfilepath"],
                            "associated_typename": row["associated_typename"],
                            "linked_created": row["linked_created_date"],
                            "linked_updated": row["linked_updated_date"]
                        }
                        for _, row in g.iterrows()
                    ]
                ).to_dict()

        # Step 3: Properties
        grouped_props = {}
        if include_properties and property_names:
            print(f"Fetching properties: {property_names}")
            all_props = []
            for table in ["vroPropertyFloat", "vroPropertyInt", "vroPropertyString", "vroPropertyBigString"]:
                query = f"""
                SELECT objectid, propertyname, value
                FROM {table}
                WHERE objectid IN ({object_ids_str})
                """
                data = self.execute(query)
                if data:
                    all_props.extend(data)

            if all_props:
                df_props = pd.DataFrame(all_props)
                df_props["propertyname_lower"] = df_props["propertyname"].str.lower()
                for obj_id, group in df_props.groupby("objectid"):
                    props = {}
                    for keyword in property_names:
                        matched = group[group["propertyname_lower"].str.contains(keyword.lower())]
                        for _, row in matched.iterrows():
                            props[row["propertyname"]] = row["value"]
                    grouped_props[obj_id] = props if props else None
                print(f" Properties mapped to {len(grouped_props)} samples.")

        # Step 4: Linked Properties
        grouped_linked_props = {}
        if include_linked_properties and property_names and not assoc_df.empty:
            linked_ids = assoc_df["linked_objectid"].unique().tolist()
            linked_ids_str = ", ".join(map(str, linked_ids))
            all_linked = []
            for table in ["vroPropertyFloat", "vroPropertyInt", "vroPropertyString", "vroPropertyBigString"]:
                query = f"""
                SELECT objectid, propertyname, value
                FROM {table}
                WHERE objectid IN ({linked_ids_str})
                """
                data = self.execute(query)
                if data:
                    all_linked.extend(data)

            if all_linked:
                df_linked = pd.DataFrame(all_linked)
                df_linked["propertyname_lower"] = df_linked["propertyname"].str.lower()
                for obj_id, group in df_linked.groupby("objectid"):
                    props = {}
                    for keyword in property_names:
                        matched = group[group["propertyname_lower"].str.contains(keyword.lower())]
                        for _, row in matched.iterrows():
                            props[row["propertyname"]] = row["value"]
                    grouped_linked_props[obj_id] = props if props else None

        # Step 5: Composition
        grouped_composition = {}
        if include_composition:
            comp_query = f"""
            SELECT sampleid, elementname, valuepercent
            FROM vroComposition
            WHERE sampleid IN ({object_ids_str})
            """
            comp_data = self.execute(comp_query)
            comp_df = pd.DataFrame(comp_data) if comp_data else pd.DataFrame()
            if not comp_df.empty:
                grouped_composition = comp_df.groupby("sampleid").apply(
                    lambda x: dict(zip(x["elementname"], x["valuepercent"]))
                ).to_dict()
                print(f"Composition info available for {len(grouped_composition)} samples.")

        # Step 6: Build summary with diagnostics
        summaries = []
        for _, row in df.iterrows():
            obj_id = row["objectid"]
            element_list = row["elements_list"]

            print(f"\n Processing Sample ID {obj_id} ({row['objectname']})")

            # Check required elements
            if required_elements:
                match = True
                for el, val_range in required_elements.items():
                    el_lower = el.lower()
                    sample_has = el_lower in [e.lower() for e in element_list]
                    if not sample_has:
                        print(f" Skipped: Missing required element '{el}'")
                        match = False
                        break
                    if val_range and obj_id in grouped_composition:
                        val = grouped_composition[obj_id].get(el)
                        if val is None or not (val >= val_range[0] and val <= val_range[1]):
                            print(f"Skipped: Element '{el}' out of range {val_range}, got {val}")
                            match = False
                            break
                if not match:
                    continue

            # Check required associated types
            assoc_objs = grouped_assoc.get(obj_id, [])
            assoc_types = {a["associated_typename"] for a in assoc_objs}
            if user_associated_typenames:
                if not set(user_associated_typenames).issubset(assoc_types):
                    print(f" Skipped: Missing associated types {user_associated_typenames} (has {assoc_types})")
                    continue
                assoc_objs = [a for a in assoc_objs if a["associated_typename"] in user_associated_typenames]

            # Include linked properties
            linked_summary_props = None
            if include_linked_properties and assoc_objs:
                temp = {}
                for linked_obj in assoc_objs:
                    lid = linked_obj["linked_objectid"]
                    props = grouped_linked_props.get(lid)
                    if props:
                        temp[lid] = props
                if temp:
                    linked_summary_props = temp

            print(f" Included sample {obj_id}")

            # Add to summary
            summary = {
            "objectid": obj_id,
            "objectname": row["objectname"],
            "formula_pretty": row["elements"],
            "elements": element_list,
            "nelements": row["nelements"],
            "objectfilepath": row["objectfilepath"],
            "created_date": row["created_date"],
            "created_by": row.get("created_by"),
            "creator_email": row.get("creator_email"),
            "associated_objects": assoc_objs,
            "properties": grouped_props.get(obj_id),
            "linked_properties": linked_summary_props,
            "composition": grouped_composition.get(obj_id, {})
        }

            summaries.append(summary)
            if save_to_json:
                os.makedirs(output_folder, exist_ok=True)
                json_path = os.path.join(output_folder, f"summary_{main_object}.json")
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(summaries, f, indent=4)
                print(f"Summary saved to {json_path}")


        print(f"\n Summary complete. {len(summaries)} samples matched your filters.")
        return summaries

    def get_summary_fields(self):
        summary_fields = {}

        # 1. Distinct associated typenames
        query_assoc = """
        SELECT DISTINCT ti.typename AS associated_typename
        FROM vroObjectinfo o

        JOIN vroObjectlinkobject olo ON o.objectid = olo.objectid
        JOIN vroObjectinfo linked_oi ON olo.linkedobjectid = linked_oi.objectid
        JOIN vroTypeinfo ti ON linked_oi.typeid = ti.typeid
        """
        assoc_data = self.execute(query_assoc)
        if assoc_data:
            df_assoc = pd.DataFrame(assoc_data)
            summary_fields["distinct_associated_typenames"] = sorted(df_assoc["associated_typename"].dropna().unique().tolist())
        else:
            summary_fields["distinct_associated_typenames"] = []

        # 2. Distinct property names
        all_propnames = set()
        for table in ["vroPropertyFloat", "vroPropertyInt", "vroPropertyString", "vroPropertyBigString"]:
            query = f"SELECT DISTINCT propertyname FROM {table}"
            data = self.execute(query)
            if data:
                df_props = pd.DataFrame(data)
                all_propnames.update(df_props["propertyname"].dropna().tolist())
        summary_fields["distinct_property_names"] = sorted(all_propnames)

        # 3. Distinct element names from composition
        query_elements = "SELECT DISTINCT elementname FROM vroComposition"
        element_data = self.execute(query_elements)
        if element_data:
            df_elem = pd.DataFrame(element_data)
            summary_fields["distinct_element_names"] = sorted(df_elem["elementname"].dropna().unique().tolist())
        else:
            summary_fields["distinct_element_names"] = []

        # 4. Distinct creator emails and usernames
        query_users = "SELECT DISTINCT email, username FROM vroAspnetusers"
        user_data = self.execute(query_users)
        if user_data:
            df_users = pd.DataFrame(user_data)
            summary_fields["distinct_creators"] = sorted(df_users["email"].dropna().unique().tolist())
            summary_fields["distinct_creator_usernames"] = sorted(df_users["username"].dropna().unique().tolist())
        else:
            summary_fields["distinct_creators"] = []
            summary_fields["distinct_creator_usernames"] = []

        return summary_fields


    def download(self, id, file_name=None):
        headers = self.get_headers()
        data = { 'id': id }
        try:
            response = requests.get(self.service_url+"download", params=data, headers=headers)
            response.raise_for_status()  # Raise exception for non-2xx status codes

            self.file_name=file_name
            if not file_name:
                file_name = self.getFilename_fromCd(response.headers.get('content-disposition'))
                #print('extracted file_name: ' + self.file_name)
            open(file_name, 'wb').write(response.content)
            return response

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None
        
    def restructure_associated_creators(self, df, strict_typenames=None):
        if df.empty:
            return df

        # Filter to only strict associated_typenames if provided
        if strict_typenames:
            df = df[df["associated_typename"].isin(strict_typenames)]

        df["creator"] = df["linked_creator_email"]
        pivot_df = df.pivot_table(
            index="main_objectid",
            columns="associated_typename",
            values="creator",
            aggfunc=lambda x: ", ".join(set(x))
        ).reset_index()

        return pivot_df

    def search(self, associated_typenames=None, main_object=None, start_date=None, end_date=None, 
            element_criteria=None, creator=None, download_folder="downloaded_files", output_filename="final.csv",
            save_location=".", strict=False):

        """
        Process data based on provided parameters.
        """
        os.makedirs(save_location, exist_ok=True)
        download_folder = os.path.join(save_location, download_folder)
        os.makedirs(download_folder, exist_ok=True)

        # Step 1: Retrieve filtered objects
        result = self.get_filtered_objects(associated_typenames, main_object, start_date, end_date, creator=creator, strict=strict)


        if not isinstance(result, tuple) or result[0].empty:
            print("No objects found in the previous step.")
            return pd.DataFrame()

        df_filtered, object_link_mapping, object_ids = result

        # Step 2: Apply element criteria filtering if provided
        if element_criteria:
            result = self.filter_samples_by_elements(object_ids, element_criteria)
            if not isinstance(result, tuple) or len(result) != 2 or result[0].empty:
                print("No matching samples found for element filtering.")
                return pd.DataFrame()
            df_samples, sample_ids = result
            df_filtered = df_filtered[df_filtered["main_objectid"].isin(sample_ids)]
        else:
            sample_ids = object_ids

      
        # Step 3: Check if composition filtering is applicable
        composition_types = {"Volume Composition", "Composition"}
        percentage_filtering_requested = element_criteria and any(isinstance(v, tuple) for v in element_criteria.values())

        # Check if user actually requested composition-related types
        user_requested_composition = any(t in composition_types for t in associated_typenames)

        if percentage_filtering_requested and user_requested_composition:
            df_final, final_filtered_mapping = self.filter_samples_by_elements_and_composition(
                sample_ids, object_link_mapping, element_criteria
            )
            df_filtered = df_filtered[df_filtered["main_objectid"].isin(final_filtered_mapping.keys())]
        elif percentage_filtering_requested:
            print("Skipping percentage filtering: user did not request composition-type objects.")
            final_filtered_mapping = object_link_mapping
        else:
            final_filtered_mapping = object_link_mapping


        if df_filtered.empty:
            print("No data matched after filtering.")
            return pd.DataFrame()

        # Create a mapping DataFrame
        df_filtered_mapping = pd.DataFrame(
            [(k, v) for k, values in final_filtered_mapping.items() for v in values],
            columns=["SampleID", "LinkedObjectID"]
        )

       
        # Filter df_filtered to keep only rows with associated_typename in the strict list
        if strict and associated_typenames:
            df_filtered = df_filtered[df_filtered["associated_typename"].isin(associated_typenames)]

        # Ensure df_filtered only includes samples with valid final mapping
        df_matched = df_filtered[df_filtered["main_objectid"].isin(final_filtered_mapping.keys())]


        # Group data by main_objectid
        grouped_data = df_matched.groupby("main_objectid").apply(lambda x: {
            "objectname": x["objectname"].iloc[0],
            "created_date": x["created_date"].iloc[0],
            "updated_date": x["updated_date"].iloc[0],
            "main_objectfilepath": x["main_objectfilepath"].iloc[0],
            "linked_objects": [
                {
                    "linked_objectid": row["linked_objectid"],
                    "linked_objectfilepath": row["linked_objectfilepath"],
                    "associated_typename": row["associated_typename"]
                }
                for _, row in x.iterrows()
            ]
        }).to_dict()

        # Save results
        json_path = os.path.join(save_location, "query_results.json")
        with open(json_path, "w", encoding="utf-8") as json_file:
            json.dump(grouped_data, json_file, indent=4)

        output_path = os.path.join(save_location, output_filename)
        df_matched.to_csv(output_path, index=False)
        print(f"Results saved to {os.path.abspath(output_path)}")


        # Step 4: Download each object's associated files into its own folder
        for objectid, metadata in grouped_data.items():
            object_folder = os.path.join(download_folder, f"object_{objectid}")
            os.makedirs(object_folder, exist_ok=True)

            for linked_obj in metadata.get("linked_objects", []):
                if strict and linked_obj.get("associated_typename") not in associated_typenames:
                    continue  # Skip if not in the allowed typenames when strict mode is on

                linked_objectid = linked_obj.get("linked_objectid")
                linked_objectfilepath = str(linked_obj.get("linked_objectfilepath", "")).strip()


                if not linked_objectfilepath or linked_objectfilepath.lower() == "nan":
                    reason = "Empty or NaN path"
                elif linked_objectfilepath.endswith(('/', '\\')) or linked_objectfilepath.count('/') < 2:
                    reason = "Invalid or incomplete path"
                else:
                    file_name = os.path.basename(linked_objectfilepath)
                    file_path = os.path.join(object_folder, file_name)
                    resp = self.download(linked_objectid, file_path)
                    if resp is not None and resp.status_code == 200:
                        continue  # success
                    reason = f"HTTP {resp.status_code if resp else 'None'}"

                with open(os.path.join(save_location, "failed_downloads.log"), "a", encoding="utf-8") as log_file:
                    log_file.write(f"{linked_objectid} - {linked_objectfilepath} - SKIPPED/FAILED ({reason})\n")
        # Export Excel with creator email per associated type
        creator_df = self.restructure_associated_creators(df_matched, strict_typenames=associated_typenames if strict else None)
        excel_path = os.path.join(save_location, "main_object_creators.xlsx")
        creator_df.to_excel(excel_path, index=False)
        print(f"Creator summary saved to {excel_path}")

        print(f"All downloads completed. Files are saved in {download_folder}")
        return df_matched


# Example usage:
if __name__ == "__main__":
    tenant_url = "https://crc1625.mdi.ruhr-uni-bochum.de/"
    api_key = "doaa.mohamed@ruhr-uni-bochum.de_36605097-dc2a-4a37-accc-05051977079b" 

    client = MatInfWebApiClient(tenant_url, api_key)

    associated_typenames = ['EDX CSV', 'Photo', 'HTTS Resistance CSV']
    main_object = 'Sample'
    start_date = '2024-01-01'
    end_date = '2024-12-31'

    element_criteria = {
       'Ag': (5, 20),
    'Pd': (5, 20),
    }

    df_filtered = client.process_data(
       associated_typenames=associated_typenames,
       main_object=main_object,
       start_date=start_date,
        end_date=end_date,
        element_criteria=element_criteria,
        strict=True
    )

    summary = client.get_summary(
        main_object="Sample",
        start_date="2024-01-01",
        end_date="2024-12-31",
        include_associated=True,
        include_properties=True,
        include_composition=True,
        property_names=["Wafer ID", "Type"]
    )

    # Save to JSON
    import json
    with open("material_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    # Or just preview
    print(json.dumps(summary[:2], indent=2))
