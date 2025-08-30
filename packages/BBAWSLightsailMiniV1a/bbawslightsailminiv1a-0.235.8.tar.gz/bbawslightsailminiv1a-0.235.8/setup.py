import os
from PlatformConnectors.PackageMaker import PackageAutomation

package = PackageAutomation(os.path.dirname(__file__))
package.auto_setup(package)

