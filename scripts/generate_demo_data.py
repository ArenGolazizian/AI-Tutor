"""Script to generate demo PDF and CSV files for testing."""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path
import csv


def create_demo_pdf(filename: str, title: str, content: str):
    """Create a simple PDF with text content."""
    from fpdf import FPDF
    
    pdf_path = Path("data/demo") / filename
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    pdf.set_font('Helvetica', '', 12)
    paragraphs = content.strip().split('\n\n')
    
    for i, para in enumerate(paragraphs):
        para = para.strip()
        if para:
            para = ' '.join(para.split())
            pdf.multi_cell(0, 5, para)
            
            if i < len(paragraphs) - 1:
                pdf.ln(3)
    
    pdf.output(str(pdf_path))
    print(f"Created {pdf_path}")


def create_demo_data():
    """Generate demo PDFs and metadata CSV."""
    
    create_demo_pdf(
        "algebra_basics.pdf",
        "Introduction to Algebra",
        """
        Algebra is a branch of mathematics that uses symbols and letters to represent numbers and quantities in formulas and equations. The word 'algebra' comes from the Arabic word 'al-jabr', which means 'reunion of broken parts'.\n\n
        Variables are symbols (usually letters like x, y, or z) that represent unknown values. For example, in the equation x + 5 = 10, the letter 'x' is a variable representing the unknown number we need to find. Variables allow us to write general rules and formulas that work for many different situations.\n\n
        An algebraic expression is a mathematical phrase that can contain numbers, variables, and operation symbols like addition, subtraction, multiplication, and division. Examples of algebraic expressions include: 3x + 2, 5y - 7, 2a + 3b, and x squared minus 4. These expressions can be simplified, combined, and manipulated using algebraic rules.\n\n
        Solving equations means finding the value of the variable that makes the equation true. For example, to solve x + 5 = 10, we subtract 5 from both sides to get x = 5. The key principle is to perform the same operation on both sides of the equation to maintain equality. This is called the balance method, because we keep the equation balanced like a scale.\n\n
        Linear equations are equations where variables are raised to the first power only. They are called 'linear' because their graph is always a straight line. The general form of a linear equation is y = mx + b, where m is the slope (how steep the line is) and b is the y-intercept (where the line crosses the y-axis). Linear equations appear frequently in real-world problems involving constant rates of change.\n\n
        Quadratic equations involve variables raised to the second power and have the general form ax squared plus bx plus c equals 0. These equations can be solved using factoring, completing the square, or the quadratic formula. The graph of a quadratic equation is a parabola, which is a U-shaped curve. Quadratic equations are used in physics to describe projectile motion and in business to model profit and revenue.\n\n
        Key skills in algebra include: simplifying expressions by combining like terms, solving for unknown variables using inverse operations, working with inequalities to show ranges of solutions, factoring polynomials into simpler expressions, and understanding functions and their graphs. Functions are special relationships where each input has exactly one output.\n\n
        Algebra is fundamental to higher mathematics and is used extensively in science, engineering, computer programming, economics, and many other fields. Mastering algebraic thinking helps develop problem-solving skills and logical reasoning that are valuable in all areas of life.
        """
    )
    
    create_demo_pdf(
        "physics_newton.pdf",
        "Newton's Laws of Motion",
        """
        Sir Isaac Newton formulated three fundamental laws that describe the relationship\nbetween a body and the forces acting upon it. These laws, published in 1687 in his\nwork 'Principia Mathematica', form the foundation of classical mechanics and revolutionized\nour understanding of motion and force.\n\n

        Newton's First Law, also known as the Law of Inertia, states that an object at rest stays\nat rest, and an object in motion stays in motion with the same speed and direction, unless\nacted upon by an unbalanced force. Inertia is the tendency of objects to resist changes in\ntheir state of motion. This is why passengers in a car lurch forward when the driver suddenly\nbrakes - their bodies want to continue moving at the same speed. The amount of inertia an\nobject has depends on its mass; objects with more mass have greater inertia.\n\n

        Newton's Second Law quantifies the relationship between force, mass, and acceleration. It\nstates that the acceleration of an object depends on the mass of the object and the amount\nof force applied. The mathematical formula is F = ma, where F is force measured in Newtons,\nm is mass in kilograms, and a is acceleration in meters per second squared. This law tells\nus that the same force applied to objects of different masses will produce different\naccelerations - a heavier object will accelerate more slowly than a lighter one.\n\n

        Newton's Third Law states that for every action, there is an equal and opposite reaction.\nWhen one object exerts a force on a second object, the second object simultaneously exerts\nan equal force in the opposite direction on the first object. These action-reaction pairs\nact on different objects. For example, when you jump, you push down on the Earth, and the\nEarth pushes up on you with equal force. Because the Earth has so much more mass than you,\nits acceleration is negligible while you accelerate upward.\n\n

        These laws apply to everyday situations. When you kick a soccer ball, you apply force\naccording to the Second Law - the harder you kick, the greater the acceleration. The ball\npushes back on your foot with equal force as described by the Third Law. And the ball keeps\nrolling until friction (an unbalanced force) slows it down, illustrating the First Law.\n\n

        Understanding Newton's laws is fundamental to physics and engineering. They help us design\nvehicles that can accelerate safely, buildings that can withstand forces like wind and\nearthquakes, and rockets that can escape Earth's gravity. These principles also extend to\nunderstanding planetary motion, how machines work, and even how to catch a ball. While\nEinstein's relativity showed that Newton's laws need modification at very high speeds or\nin strong gravitational fields, they remain extremely accurate for most everyday situations\nand continue to be essential tools in science and engineering.
        """
    )
    
    create_demo_pdf(
        "biology_cells.pdf",
        "Introduction to Cell Structure",
        """
        Cells are the fundamental units of life, serving as the building blocks of all living\norganisms. The cell theory, one of the central principles of biology, states that all\nliving things are composed of one or more cells, that cells are the basic units of\nstructure and function in organisms, and that all cells come from pre-existing cells\nthrough cell division.\n\n

        There are two main types of cells: prokaryotic and eukaryotic. Prokaryotic cells, found\nin bacteria and archaea, are simpler and lack a membrane-bound nucleus. Their genetic\nmaterial floats freely in the cytoplasm in a region called the nucleoid. Eukaryotic cells,\nfound in animals, plants, fungi, and protists, are more complex and contain a true nucleus\nenclosed by a nuclear membrane, along with numerous specialized organelles.\n\n

        The nucleus is often called the control center of the cell because it houses the cell's\nDNA, which contains the genetic instructions for making proteins and controlling cellular\nactivities. The nuclear envelope, a double membrane with pores, regulates what enters and\nexits the nucleus. Inside the nucleus, the nucleolus produces ribosomes, which are essential\nfor protein synthesis.\n\n

        Mitochondria are known as the powerhouses of the cell. These organelles generate most of\nthe cell's supply of ATP (adenosine triphosphate), which serves as the cell's energy\ncurrency. Mitochondria have their own DNA and reproduce independently within the cell,\nsupporting the theory that they originated as ancient bacteria that formed a symbiotic\nrelationship with early eukaryotic cells.\n\n

        The endoplasmic reticulum (ER) is a network of membranes involved in protein and lipid\nsynthesis. The rough ER has ribosomes attached to its surface and produces proteins that\nwill be exported from the cell or inserted into membranes. The smooth ER lacks ribosomes\nand is involved in lipid synthesis and detoxification processes.\n\n

        The Golgi apparatus, sometimes called the cell's post office, modifies, packages, and\nsorts proteins and lipids received from the ER. It adds molecular tags that direct these\nmolecules to their proper destinations, whether inside the cell or for export outside it.\n\n

        Lysosomes are the cell's recycling centers, containing digestive enzymes that break down\nworn-out organelles, cellular debris, and foreign materials. In plant cells, large\nvacuoles serve similar functions while also maintaining cell structure through turgor\npressure and storing nutrients and waste products.\n\n

        The cell membrane, or plasma membrane, is a selectively permeable barrier that controls\nwhat enters and exits the cell. Composed primarily of a phospholipid bilayer with embedded\nproteins, it maintains the cell's internal environment and allows communication with other\ncells. The cytoplasm, a gel-like substance filling the cell, contains the cytosol (liquid\ncomponent) and all organelles except the nucleus.\n\n

        Plant cells have several unique structures. Cell walls made of cellulose provide structural\nsupport and protection. Chloroplasts, containing the green pigment chlorophyll, are the\nsites of photosynthesis where light energy is converted into chemical energy in the form\nof glucose. These features enable plants to maintain rigid structures and produce their\nown food, distinguishing them from animal cells.\n\n

        Understanding cell structure is crucial for comprehending how organisms function, how\ndiseases develop, and how to develop treatments. Modern medicine, biotechnology, and\nresearch all rely on detailed knowledge of cellular components and their interactions.

        """
    )
    
    csv_path = Path("data/demo/metadata.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    metadata = [
        {
            "filename": "algebra_basics.pdf",
            "subject": "Mathematics",
            "grade_level": "8",
            "topic": "Algebra Fundamentals"
        },
        {
            "filename": "physics_newton.pdf",
            "subject": "Physics",
            "grade_level": "10",
            "topic": "Newton's Laws of Motion"
        },
        {
            "filename": "biology_cells.pdf",
            "subject": "Biology",
            "grade_level": "9",
            "topic": "Cell Structure"
        }
    ]
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "subject", "grade_level", "topic"])
        writer.writeheader()
        writer.writerows(metadata)
    
    print(f"Created {csv_path}")
    print("\nDemo data generation complete!")
    print("Files created in data/demo/:")
    print("  - algebra_basics.pdf")
    print("  - physics_newton.pdf")
    print("  - biology_cells.pdf")
    print("  - metadata.csv")


if __name__ == "__main__":
    create_demo_data()
