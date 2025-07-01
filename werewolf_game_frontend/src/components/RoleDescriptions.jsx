import React from 'react';
import { 
  Eye, Shield, Zap, Crown, Skull, 
  Users, Search, Sword, Heart,
  Crosshair, Laugh, Target
} from 'lucide-react';

const roleDescriptions = {
  // TOWN ROLES
  villager: {
    name: "Villageois",
    description: "Citoyen ordinaire du village. Votre seul pouvoir est votre vote pendant le jour pour éliminer les suspects.",
    icon: Users,
    color: "text-blue-500",
    faction: "Village"
  },
  seer: {
    name: "Voyant",
    description: "Chaque nuit, vous pouvez enquêter sur un joueur pour découvrir son rôle exact.",
    icon: Eye,
    color: "text-purple-500",
    faction: "Village"
  },
  witch: {
    name: "Sorcière",
    description: "Vous possédez deux potions : une de guérison (sauve quelqu'un) et une de poison (tue quelqu'un). Chaque potion ne peut être utilisée qu'une seule fois.",
    icon: Zap,
    color: "text-green-500",
    faction: "Village"
  },
  bodyguard: {
    name: "Garde",
    description: "Chaque nuit, vous pouvez protéger un joueur des attaques nocturnes.",
    icon: Shield,
    color: "text-yellow-500",
    faction: "Village"
  },
  hunter: {
    name: "Chasseur",
    description: "Si vous êtes éliminé, vous pouvez choisir un joueur à abattre avec vous.",
    icon: Crosshair,
    color: "text-orange-500",
    faction: "Village"
  },
  sheriff: {
    name: "Sheriff",
    description: "Chaque nuit, vous pouvez enquêter sur un joueur pour savoir s'il est 'Suspect' ou 'Non Suspect'.",
    icon: Search,
    color: "text-blue-600",
    faction: "Village"
  },
  investigator: {
    name: "Investigateur",
    description: "Chaque nuit, vous obtenez des indices sur le type de rôle d'un joueur en découvrant son groupe d'appartenance.",
    icon: Search,
    color: "text-indigo-500",
    faction: "Village"
  },
  // 🆕 PHASE 3 - RÔLES DÉFENSIFS TOWN
  bodyguard_new: {
    name: "Bodyguard",
    description: "Protection sacrificielle : vous mourrez à la place de votre cible si elle est attaquée. Vous avez un gilet pare-balles pour survivre à une attaque.",
    icon: Shield,
    color: "text-cyan-500",
    faction: "Village"
  },
  veteran: {
    name: "Veteran",
    description: "Vous pouvez vous mettre en alerte 3 fois par partie. En alerte, vous tuez tous ceux qui vous visitent cette nuit.",
    icon: Sword,
    color: "text-red-600",
    faction: "Village"
  },
  doctor: {
    name: "Doctor",
    description: "Chaque nuit, vous pouvez soigner un joueur (pas vous-même) pour le protéger des attaques. Soins illimités.",
    icon: Heart,
    color: "text-pink-500",
    faction: "Village"
  },
  
  // 🆕 PHASE 4 - RÔLES NEUTRES
  survivor: {
    name: "Survivor",
    description: "Votre seul objectif est de survivre jusqu'à la fin de la partie, peu importe qui gagne. Vous avez 4 gilets de protection à utiliser la nuit.",
    icon: Shield,
    color: "text-gray-500",
    faction: "Neutre"
  },
  serial_killer: {
    name: "Serial Killer",
    description: "Tueur indépendant qui doit éliminer tous les autres joueurs pour gagner. Vous pouvez tuer chaque nuit ou rester prudent pour vous défendre.",
    icon: Target,
    color: "text-red-800",
    faction: "Neutre"
  },
  jester: {
    name: "Jester",
    description: "Votre objectif unique est d'être lynché par le village pendant le jour. Si vous y parvenez, vous gagnez immédiatement la partie !",
    icon: Laugh,
    color: "text-purple-600",
    faction: "Neutre"
  },

  // MAFIA ROLES
  werewolf: {
    name: "Loup-Garou",
    description: "Créature maléfique qui dévore les villageois la nuit. Vous pouvez communiquer avec les autres loups-garous.",
    icon: Users,
    color: "text-red-500",
    faction: "Mafia"
  },
  // 🆕 PHASE 1 - RÔLES MAFIA
  godfather: {
    name: "Godfather",
    description: "Chef de la famille Mafia. Vous coordonnez les éliminations et êtes immunisé aux investigations du Sheriff. Vous avez une défense basique.",
    icon: Crown,
    color: "text-yellow-600",
    faction: "Mafia"
  },
  mafioso: {
    name: "Mafioso",
    description: "Bras armé de la famille. Vous exécutez les ordres du Godfather et éliminez les cibles désignées chaque nuit.",
    icon: Skull,
    color: "text-red-700",
    faction: "Mafia"
  },
  blackmailer: {
    name: "Blackmailer",
    description: "Maître du chantage. Chaque nuit, vous pouvez empêcher un joueur de parler le jour suivant en le faisant chanter.",
    icon: Zap,
    color: "text-purple-700",
    faction: "Mafia"
  },
  consigliere: {
    name: "Consigliere",
    description: "Espion de la famille. Chaque nuit, vous pouvez enquêter sur un joueur pour découvrir son rôle exact, sans immunité.",
    icon: Eye,
    color: "text-indigo-700",
    faction: "Mafia"
  }
};

export function RoleDescription({ role }) {
  const roleInfo = roleDescriptions[role];
  
  if (!roleInfo) {
    return <div>Rôle inconnu : {role}</div>;
  }

  const IconComponent = roleInfo.icon;
  
  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <div className="flex items-center gap-3 mb-3">
        <IconComponent className={`h-6 w-6 ${roleInfo.color}`} />
        <div>
          <h3 className="text-lg font-bold text-white">{roleInfo.name}</h3>
          <span className={`text-sm px-2 py-1 rounded ${
            roleInfo.faction === 'Village' ? 'bg-blue-900 text-blue-200' :
            roleInfo.faction === 'Mafia' ? 'bg-red-900 text-red-200' :
            'bg-gray-900 text-gray-200'
          }`}>
            {roleInfo.faction}
          </span>
        </div>
      </div>
      <p className="text-gray-300 leading-relaxed">{roleInfo.description}</p>
    </div>
  );
}

export default RoleDescription;