"""
Main chat handler for construction project management chatbot.
"""
import json
import re
import logging
import difflib
from typing import List, Dict, Optional
from .gemini_client import GeminiClient
from database.db_connector import DatabaseConnector
from database.schema_extractor import SchemaExtractor

logger = logging.getLogger(__name__)

class ChatHandler:
    def __init__(self, api_key: str, db_config: Dict):
        """Initialize chat handler."""
        self.gemini = GeminiClient(api_key)
        self.db = DatabaseConnector(db_config)
        self.schema_extractor = SchemaExtractor(db_config)
        
        # Get formatted schema for AI context
        self.schema_info = self.schema_extractor.get_formatted_schema_prompt()
        rows = self.db.execute_query("SELECT name FROM projects;")
        self.all_project_names = [r['name'] for r in rows]
        
        # System prompt for construction management context
        self.system_prompt = f"""
You are a professional construction project management assistant. 
 **When you generate SQL you must:**
 - Match ​all​ text-based filters (project names, selection items, etc.) case-insensitively.  
   For example: `WHERE p.name ILIKE '%Cabot-1b%'` ​or​ `WHERE UPPER(p.name)=UPPER('cabot-1b')`.
   (No exact‐case `=` checks on raw literals, ever.)
 - Always use `ILIKE` or `UPPER(col)=UPPER(literal)` for every string comparison.
 - If the user asks about “subphase” or “next subphase,” generate the appropriate JOIN+ORDER+LIMIT.

Available Database Schema:
{self.schema_info}

Supported Question Categories (answer *only* these, using live DB data):
1. **Selection Management**  
   - What are the open selection items for X project?  
   - How overdue is X selection?  
   - What selections are coming up in the next 2 weeks?  
2. **Project Phase Tracking**  
   - What stage and phase is X project in?  
   - What items still need to be completed in the current phase?  
3. **Walkthrough Management**  
   - Do any PD Walkthroughs need to be scheduled?  
   - Do any Client walkthroughs need to be scheduled?  
   - Has the most recent client walkthrough been completed?  
4. **Procurement Tracking**  
   - What still needs to be bought out?  
   - What trades still need a purchase order issued?  
5. **Financial Milestone Tracking**  
   - What payment milestone is project X currently at?  
   - What projects can be billed this week?  
   - Has payment milestone #2 been issued? 
6. **Budget / Invoicing**  
  - Whats the budget status for all projects?  
  - What invoices have been issued for project X?
Additional Quick Queries:  
   - What subphase is X in?  
   - What is the next subphase in X?  
   - What is the percent completed of X subphase?  
   - What selection is X on?  
   - What selections are overdue or coming up on X?  
   - Has the PM completed the PD walkthrough on X subphase?  

If the user asks *any other* question, respond with a single, to-the-point sentence—no extra detail or speculation if the relevant data is not found from the database.  

Response Guidelines:
- Always use Markdown bullets or short tables.  
- Bold key items (project names, dates, percentages).  
- Do not suggest anything not directly in the database.
- **Budget & Invoicing**: invoices are stored in the `invoices` table, join on `projects.client_id → leads.id → invoices.customer_id`
- If no high-level summary applies, fall back to listing every column and its value


"""
    def process_query(self, user_message: str, conversation_history: List[Dict] = None) -> Dict:
        """Process any user query: first catch project or budget requests, 
        otherwise fall back to Gemini+SQL or pure Gemini."""
        text = user_message.strip()

        # ─── 0) PROJECT DETAIL INTERCEPT ────────────────────────────────
        #  a) Full project summary ("details of CABOT-1B project")
        m_detail = re.search(
            r"\bdetails? of\s+([A-Za-z0-9\-]+)\s+project",
            text,
            re.IGNORECASE
        )
        if m_detail:
            # uppercase the key so you get an exact match in your SQL
            return self._handle_project_summary(m_detail.group(1).upper())

        #  b) Phase‐status / progress ("status of JAIN-1B", "progress of ELMGROVE-1B")
        m_phase = re.search(
            r"\b(?:status|progress) of\s+([A-Za-z0-9\-]+)",
            text,
            re.IGNORECASE
        )
        if m_phase:
            return self.get_project_phase_details(m_phase.group(1).upper())

        # ─── 1) BUDGET / INVOICING INTERCEPT ─────────────────────────────
        if re.search(r"budget status for all projects", text, re.IGNORECASE):
            return self.get_budget_status_all()

        m_budget = re.search(
            r"budget status for\s+([A-Za-z0-9\-]+)\s+project",
            text,
            re.IGNORECASE
        )
        if m_budget:
            return self.get_project_budget_details(m_budget.group(1).upper())

        # ─── 2) FALL BACK TO GEMINI + GENERIC SQL ────────────────────────
        try:
            intent = self.gemini.analyze_query_intent(text, self.schema_info)
            if intent.get('needs_database', True):
                sql_query = self.gemini.generate_sql_query(text, self.schema_info)
                try:
                    results = self.db.execute_safe(sql_query)
                    formatted = self.gemini.format_query_results(text, sql_query, results)
                    return {
                        "message": formatted,
                        "success": True,
                        "sql_query": sql_query,
                        "results_count": len(results)
                    }
                except Exception as sql_err:
                    logger.error(f"SQL execution error: {sql_err}")
                    fallback = self.gemini.generate_response(
                        text, conversation_history, self.system_prompt
                    )
                    return {
                        "message": fallback,
                        "success": True,
                        "error": str(sql_err)
                    }

            # pure LLM path
            resp = self.gemini.generate_response(text, conversation_history, self.system_prompt)
            return {"message": resp, "success": True, "no_database": True}

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "message": "I’m sorry—something went wrong. Could you rephrase?",
                "success": False,
                "error": str(e)
            }

    
    # def process_query(self, 
    #                   user_message: str, 
    #                   conversation_history: List[Dict] = None) -> Dict:
    #     """Process user query and return formatted response."""
    #     try:
    #         # ➤ Budget‐status intercepts
    #         text = user_message.strip()
    #         if re.search(r"budget status for all projects", text, re.IGNORECASE):
    #             return self.get_budget_status_all()

    #         m_budget = re.search(r"budget status for\s+([A-Za-z0-9\-]+)\s+project", text, re.IGNORECASE)
    #         if m_budget:
    #             project_key = m_budget.group(1).upper()
    #             return self.get_project_budget_details(project_key)

    #         # 0) Intercept “status of X” or “progress of X” → phase details
    #         m_phase = re.search(
    #             r"\b(?:status|progress) of\s+([A-Za-z0-9\-]+)",
    #             text,
    #             re.IGNORECASE
    #         )
    #         if m_phase:
    #             project_key = m_phase.group(1).upper()
    #             return self.get_project_phase_details(project_key)

    #         # 0.1) Intercept “detail(s) of X” → full project summary
    #         m_detail = re.search(
    #             r"\bdetails? of\s+([A-Za-z0-9\-]+)",
    #             text,
    #             re.IGNORECASE
    #         )
    #         if m_detail:
    #             project_key = m_detail.group(1).upper()
    #             return self.get_project_summary(project_key)

    #         # 1) Ask Gemini if we need a DB query
    #         intent = self.gemini.analyze_query_intent(text, self.schema_info)
    #         if intent.get('needs_database', True):
    #             sql_query = self.gemini.generate_sql_query(text, self.schema_info)
    #             try:
    #                 results = self.db.execute_safe(sql_query)
    #                 formatted = self.gemini.format_query_results(text, sql_query, results)
    #                 return {
    #                     "message": formatted,
    #                     "success": True,
    #                     "sql_query": sql_query,
    #                     "results_count": len(results)
    #                 }
    #             except Exception as sql_err:
    #                 logger.error(f"SQL execution error: {sql_err}")
    #                 fallback = self.gemini.generate_response(
    #                     text, conversation_history, self.system_prompt
    #                 )
    #                 return {
    #                     "message": fallback + "\n\n*Note: Unable to retrieve database information.*",
    #                     "success": True,
    #                     "error": str(sql_err)
    #                 }

    #         # 2) No‐database fallback
    #         resp = self.gemini.generate_response(text, conversation_history, self.system_prompt)
    #         return {"message": resp, "success": True, "no_database": True}

    #     except Exception as e:
    #         logger.error(f"Error processing query: {e}")
    #         return {
    #             "message": "I apologize for the error. Please try rephrasing your question.",
    #             "success": False,
    #             "error": str(e)
    #         }



        
    def get_project_phase_details(self, project_name: str) -> Dict:
        """Get the status of each phase for a given project."""
        try:
            sql = f"""
            SELECT
              p.name        AS project_name,
              ph.name       AS phase_name,
              ph."order"    AS phase_order,
              ph.status     AS phase_status
            FROM projects p
            JOIN phases ph
              ON ph.project_id = p.id
            WHERE p.name ILIKE %s
            ORDER BY ph."order";
            """
            rows = self.db.execute_query(sql, (f"%{project_name}%",))
            if not rows:
                return {"message": f"No phases found for project '{project_name}'.", "success": True}

            # Build markdown table
            header = "| Phase | Order | Status |\n|---|---|---|\n"
            body = "\n".join(
                f"| {r['phase_name']} | {r['phase_order']} | {r['phase_status']} |"
                for r in rows
            )
            return {
                "message": f"**Phase Status for {rows[0]['project_name']}:**\n\n" + header + body,
                "success": True
            }
        except Exception as e:
            logger.error(f"Error fetching phase details: {e}")
            return {"message": "Sorry, I couldn’t fetch the phase details right now.", "success": False}
        
    def get_budget_status(self) -> Dict:
        """
        Return total invoiced amount per project by joining projects → leads → invoices.
        """
        try:
            sql = """
            SELECT
              p.name                     AS project_name,
              COALESCE(SUM(i."totalAmount"),0)::decimal(12,2) AS total_invoiced,
              COUNT(i.id)                AS invoice_count
            FROM projects p
            LEFT JOIN leads l       ON p.client_id = l.id
            LEFT JOIN invoices i    ON i.customer_id = l.id
            GROUP BY p.name
            ORDER BY total_invoiced DESC;
            """
            rows = self.db.execute_query(sql)
            if not rows:
                return {"message": "No invoice data found for any project.", "success": True}

            # build markdown table
            header = "| Project | # Invoices | Total Invoiced |\n|---|---|---|\n"
            body = "\n".join(
                f"| **{r['project_name']}** | {r['invoice_count']} | ${r['total_invoiced']} |"
                for r in rows
            )
            return {
                "message": "**Budget Status for All Projects**\n\n" + header + body,
                "success": True
            }

        except Exception as e:
            logger.error(f"Error fetching budget status: {e}")
            return {
                "message": "Sorry, I couldn’t retrieve budget status right now.",
                "success": False
            }
    def get_budget_status_all(self) -> Dict:
        """Return # of invoices and total invoiced per project."""
        sql = """
        SELECT
          p.name AS project,
          COUNT(i.id)                            AS invoice_count,
          COALESCE(SUM(i."totalAmount"), 0)::numeric(12,2) AS total_invoiced
        FROM projects p
        LEFT JOIN leads  l ON p.client_id   = l.id
        LEFT JOIN invoices i ON i.customer_id = l.id
        GROUP BY p.name
        ORDER BY total_invoiced DESC;
        """
        rows = self.db.execute_query(sql)
        header = "| Project | # Invoices | Total Invoiced |\n|---|---|---|\n"
        body = "\n".join(
            f"| **{r['project']}** | {r['invoice_count']} | ${r['total_invoiced']} |"
            for r in rows
        )
        return {"message": f"**Budget Status for All Projects**\n\n{header}{body}", "success": True}

    def get_project_budget_details(self, project_key: str) -> Dict:
        """Return every invoice for a single project."""
        sql = """
        SELECT
          p.name            AS project,
          i."invoiceNumber" AS invoice_no,
          i."totalAmount"   AS amount,
          i."paymentStatus" AS status,
          TO_CHAR(i."paymentDate",'YYYY-MM-DD') AS paid_on
        FROM projects p
        JOIN leads    l ON p.client_id    = l.id
        JOIN invoices i ON i.customer_id = l.id
        WHERE p.name = %s
        ORDER BY i."paymentDate" DESC;
        """
        rows = self.db.execute_query(sql, (project_key,))
        if not rows:
            return {
                "message": f"No invoices found for project **{project_key}**.",
                "success": True
            }

        header = "| Invoice # | Amount | Status | Paid On |\n|---|---|---|---|\n"
        body = "\n".join(
            f"| {r['invoice_no']} | ${r['amount']} | {r['status']} | {r['paid_on']} |"
            for r in rows
        )
        return {
            "message": f"**Invoices for {rows[0]['project']}:**\n\n{header}{body}",
            "success": True
        }

    def _handle_project_summary(self, raw_name: str) -> Dict:
        """
        1) Try exact summary
        2) Fuzzy-match against self.all_project_names
        3) If no close match, list all projects
        """
        # 1) exact
        resp = self.get_project_summary(raw_name)
        if resp.get("success"):
            return resp
        
        # 2) fuzzy
        candidates = [n.upper() for n in self.all_project_names]
        matches = difflib.get_close_matches(raw_name.upper(), candidates, n=3, cutoff=0.6)
        if matches:
            suggestions = [n for n in self.all_project_names if n.upper() in matches]
            list_md = "\n".join(f"- **{n}**" for n in suggestions)
            return {
                "message": (
                    f"I couldn't find an exact project named '{raw_name}'.\n"
                    "Did you mean:\n\n" + list_md
                ),
                "success": True
            }
        
        # 3) list all
        full_list = "\n".join(f"- **{n}**" for n in self.all_project_names)
        return {
            "message": (
                f"No project matches '{raw_name}'. Here are all available projects:\n\n" + full_list
            ),
            "success": True
        }

    
    
    def get_project_summary(self, project_name: str) -> Dict:
        """Get comprehensive project summary as a Markdown message."""
        try:
            # 1) Try to load exactly that project (case‐insensitive)
            sql_project = """
            SELECT
              p.id,
              p.name                             AS project_name,
              pt.name                            AS template_name,
              CONCAT(u."firstName",' ',u."lastName") AS designer_name,
              CONCAT(l."firstName",' ',l."lastName") AS client_name,
              TO_CHAR(p."startDate", 'YYYY-MM-DD')    AS start_date,
              p."percentComplete"                 AS stored_percent_complete,
              TO_CHAR(p."createdAt", 'YYYY-MM-DD')    AS created_at
            FROM projects p
            LEFT JOIN project_templates pt
              ON p.project_template_id = pt.id
            LEFT JOIN users u
              ON p.project_designer_id = u.id
            LEFT JOIN leads l
              ON p.client_id = l.id
            WHERE UPPER(p.name) = %s
            LIMIT 1;
            """
            proj_rows = self.db.execute_query(sql_project, (project_name.upper(),))
            if not proj_rows:
                # 1a) suggestions on partial match
                suggestions = self.db.execute_query(
                    "SELECT name FROM projects WHERE name ILIKE %s ORDER BY name LIMIT 5",
                    (f"%{project_name}%",)
                )
                if suggestions:
                    items = "\n".join(f"- **{r['name']}**" for r in suggestions)
                    return {
                        "message": (
                            f"I couldn't find an exact project named **{project_name}**.\n"
                            "Did you mean:\n\n" + items
                        ),
                        "success": True
                    }
                # 1b) full list fallback
                all_names = self.db.execute_query("SELECT name FROM projects ORDER BY name", ())
                items = "\n".join(f"- **{r['name']}**" for r in all_names)
                return {
                    "message": (
                        f"No project matches **{project_name}**. Here are all available projects:\n\n"
                        + items
                    ),
                    "success": True
                }

            # 2) We have an exact match
            project = proj_rows[0]

            # 3) Load phase/subphase counts for % done
            phase_q = """
            SELECT
              ph.name   AS phase_name,
              ph."order" AS phase_order,
              ph.status AS phase_status,
              COUNT(sp.*) FILTER (WHERE sp.status='Completed') AS done,
              COUNT(sp.*) AS total
            FROM phases ph
            LEFT JOIN subphases sp
              ON sp.phase_id = ph.id
            WHERE ph.project_id = %s
            GROUP BY ph.id
            ORDER BY ph."order";
            """
            phases = self.db.execute_query(phase_q, (project["id"],))

            # 4) Build the Markdown response
            header = (
                f"**Project:** {project['project_name']}  \n"
                f"- **Template:** {project['template_name'] or '—'}  \n"
                f"- **Designer:** {project['designer_name'] or '—'}  \n"
                f"- **Client:** {project['client_name'] or '—'}  \n"
                f"- **Start Date:** {project['start_date'] or '—'}  \n"
                f"- **Overall % Complete:** {project['stored_percent_complete']}%  \n"
                f"- **Created At:** {project['created_at']}  \n\n"
                "**Phases:**\n\n"
                "| Phase | Order | Status | % Done |\n"
                "|-------|-------|--------|--------|\n"
            )

            rows_md = ""
            for ph in phases:
                pct = f"{round(ph['done'] / ph['total'] * 100)}%" if ph["total"] > 0 else "0%"
                rows_md += (
                    f"| {ph['phase_name']} | {ph['phase_order']} | "
                    f"{ph['phase_status']} | {pct} |\n"
                )

            return {"message": header + rows_md, "success": True}

        except Exception as e:
            logger.error(f"Error getting project summary: {e}")
            return {
                "message": "Sorry, I couldn’t fetch the project summary right now.",
                "success": False
            }
    
    def search_across_database(self, search_term: str) -> Dict:
        """Search across multiple tables for relevant information."""
        try:
            results = {}
            
            # Search projects
            project_query = f"""
            SELECT name, 'project' as type, id
            FROM projects
            WHERE name ILIKE '%{search_term}%'
            LIMIT 10;
            """
            results['projects'] = self.db.execute_query(project_query)
            
            # Search phases
            phase_query = f"""
            SELECT ph.name, 'phase' as type, ph.id, p.name as project_name
            FROM phases ph
            JOIN projects p ON ph.project_id = p.id
            WHERE ph.name ILIKE '%{search_term}%'
            LIMIT 10;
            """
            results['phases'] = self.db.execute_query(phase_query)
            
            # Search subphases/tasks
            task_query = f"""
            SELECT sp.name, 'task' as type, sp.id, ph.name as phase_name, p.name as project_name
            FROM subphases sp
            JOIN phases ph ON sp.phase_id = ph.id
            JOIN projects p ON ph.project_id = p.id
            WHERE sp.name ILIKE '%{search_term}%'
            LIMIT 10;
            """
            results['tasks'] = self.db.execute_query(task_query)
            
            return {
                "results": results,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error searching database: {e}")
            return {
                "error": str(e),
                "success": False
            }
    
    def get_dashboard_data(self) -> Dict:
        """Get dashboard summary data for overview."""
        try:
            dashboard_query = """
            SELECT 
                COUNT(DISTINCT p.id) as total_projects,
                COUNT(CASE WHEN p."percentComplete" < 100 THEN 1 END) as active_projects,
                COUNT(CASE WHEN p."percentComplete" = 100 THEN 1 END) as completed_projects,
                ROUND(AVG(p."percentComplete"), 2) as avg_completion,
                COUNT(DISTINCT ph.id) as total_phases,
                COUNT(DISTINCT sp.id) as total_tasks,
                COUNT(CASE WHEN sp.status = 'Completed' THEN 1 END) as completed_tasks
            FROM projects p
            LEFT JOIN phases ph ON p.id = ph.project_id
            LEFT JOIN subphases sp ON ph.id = sp.phase_id;
            """
            
            dashboard_data = self.db.execute_query(dashboard_query)[0]
            
            # Get recent activity
            recent_query = """
            SELECT 
                p.name as project_name,
                sp.name as task_name,
                sp.status,
                sp."updatedAt" as last_update
            FROM subphases sp
            JOIN phases ph ON sp.phase_id = ph.id
            JOIN projects p ON ph.project_id = p.id
            WHERE sp."updatedAt" >= CURRENT_DATE - INTERVAL '7 days'
            ORDER BY sp."updatedAt" DESC
            LIMIT 10;
            """
            
            recent_activity = self.db.execute_query(recent_query)
            
            return {
                "dashboard": dashboard_data,
                "recent_activity": recent_activity,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {
                "error": str(e),
                "success": False
            }