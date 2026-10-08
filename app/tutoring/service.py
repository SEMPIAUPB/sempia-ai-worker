from app.llm.gemini_adapter import GeminiAdapter
from app.common.schemas import TutoringRequest, TutoringResponse

class TutoringService:
    def __init__(self):
        self.llm = GeminiAdapter()

    def generate_hint(self, request: TutoringRequest) -> TutoringResponse:
        # Enforce progressive hinting limit
        if len(request.previous_hints) >= 5:
            return TutoringResponse(
                probable_error_type="Limit reached",
                cause_explanation="You have reached the maximum number of hints for this exercise.",
                programming_concept="N/A",
                pedagogical_recommendation="Please review the material or ask an instructor.",
                confidence_level="High",
                hint_text="Maximum of 5 hints reached. No more hints can be generated.",
                can_resubmit=False
            )

        prompt = f"""
        Act as an expert programming tutor.
        The student is solving the following exercise:
        {request.exercise_statement}
        
        Student's code in {request.language}:
        {request.student_code}
        
        The judge gave the verdict: {request.judge_verdict}
        Compiler/Runtime messages: {request.compiler_or_runtime_messages}
        Failed test cases: {request.failed_test_cases}
        
        Previous hints given to the student: {request.previous_hints}
        
        Generate a JSON response with the following schema:
        {{
            "probable_error_type": "string",
            "approximate_line": "string or null",
            "cause_explanation": "string",
            "programming_concept": "string",
            "pedagogical_recommendation": "string",
            "confidence_level": "string",
            "hint_text": "string",
            "can_resubmit": boolean
        }}
        
        Rules for hint_text:
        - Do not give the full solution.
        - Give a progressive hint. Since there were {len(request.previous_hints)} previous hints, make this hint slightly more specific than the last one, but still educational.
        """
        
        try:
            response_data = self.llm.generate_tutoring_hint(prompt)
            return TutoringResponse(**response_data)
        except Exception as e:
            # Fallback heuristic logic if AI is unavailable (e.g. 503 or 429)
            print(f"AI Tutoring failed: {e}. Using fallback mechanism.")
            return self._generate_fallback_hint(request, str(e))

    def _generate_fallback_hint(self, request: TutoringRequest, error_msg: str) -> TutoringResponse:
        verdict = request.judge_verdict
        
        probable_error_type = "Desconocido"
        cause = "Tuvimos problemas conectando con la IA Tutora, pero aquí tienes una evaluación automática basada en el veredicto del juez."
        concept = "Conceptos generales"
        recommendation = "Revisa tu código paso a paso o usa casos de prueba más simples."
        hint = "Verifica la sintaxis, límites de arreglos o tipos de datos que estás usando."
        
        if verdict == "COMPILATION_ERROR":
            probable_error_type = "Error de Sintaxis o Compilación"
            concept = "Sintaxis del lenguaje"
            cause = "El código no compila. Suele faltar un punto y coma, una llave, o hay un tipo de dato incorrecto."
            recommendation = "Revisa los mensajes del compilador detenidamente para encontrar la línea con error."
            hint = "¡Tu código tiene un error de sintaxis! Revisa si te falta cerrar llaves '{}', paréntesis '()', o comillas. Si usas un lenguaje tipado, revisa los tipos."
            
        elif verdict == "RUNTIME_ERROR":
            probable_error_type = "Excepción en Tiempo de Ejecución"
            concept = "Manejo de Excepciones / Estructuras de Datos"
            cause = "El código falló mientras se ejecutaba. Posible división por cero, acceso fuera de los límites de un arreglo, o uso de puntero nulo."
            recommendation = "Verifica los índices de tus arreglos y asegúrate de no hacer operaciones inválidas con objetos nulos."
            hint = "El programa se cerró inesperadamente. Revisa si estás accediendo a una posición inválida en un arreglo o matriz, o dividiendo por cero."
            
        elif verdict == "TIME_LIMIT_EXCEEDED":
            probable_error_type = "Límite de Tiempo Excedido (TLE)"
            concept = "Complejidad Algorítmica (Big O)"
            cause = "Tu algoritmo es correcto para casos pequeños pero es ineficiente y demasiado lento para los más grandes."
            recommendation = "Intenta buscar una estructura de datos más eficiente (ej. Tablas Hash en vez de Arreglos) o elimina ciclos anidados innecesarios."
            hint = "¡Tu solución está tomando demasiado tiempo! Intenta optimizarla: si usas bucles anidados O(N^2), piensa si puedes resolverlo en O(N) u O(N log N)."
            
        elif verdict == "WRONG_ANSWER":
            probable_error_type = "Respuesta Incorrecta (Lógica)"
            concept = "Lógica de Programación"
            cause = "El código compila y corre rápido, pero no produce el resultado esperado para algunos casos."
            recommendation = "Simula tu algoritmo en papel con casos límite (ej. arreglos vacíos, números negativos, 0)."
            
            code_lower = request.student_code.lower() if request.student_code else ""
            if "null" in code_lower or "none" in code_lower:
                hint = "La respuesta generada no coincide. Revisa si estás manejando correctamente los casos donde la entrada es vacía o se debe retornar nulo."
            elif "for" in code_lower or "while" in code_lower:
                hint = "La lógica de tus ciclos no produce el resultado exacto. ¿Has revisado las condiciones de parada o si omites el primer o último elemento accidentalmente?"
            else:
                hint = "La respuesta generada no coincide con lo esperado. Revisa si estás entendiendo correctamente el problema o si estás ignorando casos especiales/extremos."
                
        elif verdict == "MEMORY_LIMIT_EXCEEDED":
            probable_error_type = "Límite de Memoria Excedido"
            concept = "Gestión de Memoria"
            cause = "Estás guardando demasiados datos a la vez, creando matrices muy grandes o hay una recursión infinita."
            recommendation = "No almacenes todo si no es necesario, a veces solo necesitas calcular resultados al vuelo."
            hint = "Tu código usa demasiada memoria. Asegúrate de no crear estructuras de datos gigantes si no son requeridas, y revisa que tu recursión termine correctamente."

        return TutoringResponse(
            probable_error_type=probable_error_type,
            cause_explanation=cause,
            programming_concept=concept,
            pedagogical_recommendation=recommendation,
            confidence_level="Medium (Fallback)",
            hint_text=hint + " (Pista Automática)",
            can_resubmit=True
        )
