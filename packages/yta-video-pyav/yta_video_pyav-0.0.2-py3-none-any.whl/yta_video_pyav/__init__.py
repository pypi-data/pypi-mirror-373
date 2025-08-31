"""
Module to include video handling with PyAv.

Interesting information:
| Abrev.  | Nombre completo            | Uso principal                          |
| ------- | -------------------------- | -------------------------------------- |
| VAO     | Vertex Array Object        | Esquema de datos de vértices           |
| VBO     | Vertex Buffer Object       | Datos crudos de vértices en GPU        |
| FBO     | Frame Buffer Object        | Renderizar fuera de pantalla           |
| UBO     | Uniform Buffer Object      | Variables `uniform` compartidas        |
| EBO/IBO | Element / Index Buffer Obj | Índices para reutilizar vértices       |
| PBO     | Pixel Buffer Object        | Transferencia rápida de imágenes       |
| RBO     | Render Buffer Object       | Almacén intermedio (profundidad, etc.) |
"""
def main():
    from yta_video_pyav.tests import video_modified_stored

    video_modified_stored()


if __name__ == '__main__':
    main()